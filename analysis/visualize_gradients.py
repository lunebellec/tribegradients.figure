from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from nilearn.datasets import fetch_atlas_schaefer_2018, load_fsaverage
from nilearn.surface import SurfaceImage
from surfplot import Plot


def _fetch_atlas_data(data_dir):
    schaefer_atlas = fetch_atlas_schaefer_2018(n_rois=1000, yeo_networks=7, data_dir=data_dir)
    return schaefer_atlas, load_fsaverage(data_dir=data_dir)


def _atlas_surface_labels(schaefer_atlas, fsaverage):
    surf = SurfaceImage.from_volume(mesh=fsaverage["pial"], volume_img=schaefer_atlas['maps'],
                                    interpolation='nearest_most_frequent')
    left = np.round(surf.data.parts['left']).astype(int)
    right = np.round(surf.data.parts['right']).astype(int)
    return left, right


def _setup_atlas(data_dir: Path):
    schaefer_atlas, fsaverage = _fetch_atlas_data(data_dir)
    atlas_labels = _atlas_surface_labels(schaefer_atlas, fsaverage)
    lh_path = str(fsaverage['inflated'].parts['left'].file_path)
    rh_path = str(fsaverage['inflated'].parts['right'].file_path)
    return atlas_labels, lh_path, rh_path


def _grad_to_vertices(grad_values, labels):
    out = np.zeros(len(labels))
    mask = labels > 0
    out[mask] = grad_values[labels[mask] - 1]
    return out


def _interpolate_gradients(gradients, atlas_labels):
    left_labels, right_labels = atlas_labels
    return [
        (_grad_to_vertices(gradients[:, i], left_labels),
         _grad_to_vertices(gradients[:, i], right_labels))
        for i in range(min(4, gradients.shape[1]))
    ]


def _render_gradient(lh_data, rh_data, lh_path, rh_path, cmap, vmin=-0.08, vmax=0.08):
    p = Plot(surf_lh=lh_path, surf_rh=rh_path,
             layout='grid', views=['lateral', 'medial'],
             size=(400, 400), zoom=1.2)
    p.add_layer({'left': lh_data, 'right': rh_data}, cmap=cmap, cbar=False,
                color_range=(vmin, vmax))
    rendered = p.render()
    rendered._check_offscreen()
    img = rendered.to_numpy(transparent_bg=False, scale=(2, 2))
    rendered.close()
    return img


def _save_colorbar(output_dir, cmap="viridis_r", vmin=-0.08, vmax=0.08):
    cbar_path = output_dir / "colorbar.png"
    if cbar_path.exists():
        return
    fig, ax = plt.subplots(figsize=(4, 0.4))
    fig.subplots_adjust(bottom=0.5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    fig.colorbar(sm, cax=ax, orientation='horizontal')
    plt.savefig(cbar_path, dpi=100, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
    print(f"  saved {cbar_path}")


def _save_gradient_map(gradients, output_dir, subject, movie, chunk_label, atlas_labels, lh_path, rh_path, cmap="viridis_r"):
    vmin, vmax = -0.08, 0.08
    surf_data = _interpolate_gradients(gradients, atlas_labels)
    for i, (lh, rh) in enumerate(surf_data):
        grad_path = output_dir / f"subject-{_sanitize_sub(subject)}-movie-{movie}_gradient-{i + 1}_chunk-{chunk_label}.png"
        if grad_path.exists():
            print(f"  {grad_path} already exist, skipped")
            continue
        img = _render_gradient(lh, rh, lh_path, rh_path, cmap, vmin, vmax)
        h, w = img.shape[:2]
        fig, ax = plt.subplots(1, 1, figsize=(w / 200, h / 200))
        ax.imshow(img)
        ax.axis('off')
        plt.savefig(grad_path, dpi=100, bbox_inches='tight', pad_inches=0.05)
        plt.close(fig)
        print(f"    saved {grad_path}")


def _process_chunks(subject, movie, movie_gm, movie_labels, output_dir, atlas_labels, lh_path, rh_path):
    for chunk_gm, label in zip(movie_gm, movie_labels):
        chunk = label.rsplit('_', 1)[1].zfill(2)
        _save_gradient_map(chunk_gm, output_dir, subject, movie, chunk, atlas_labels, lh_path, rh_path)

def _process_movie(subject, movie, movie_gm, movie_labels, output_dir, atlas_labels, lh_path, rh_path, smoke):
    _save_gradient_map(
            movie_gm.mean(axis=0), output_dir, subject, movie, "average", atlas_labels, lh_path, rh_path
        )
    if not smoke:
        _process_chunks(subject, movie, movie_gm, movie_labels, output_dir, atlas_labels, lh_path, rh_path)

def _sanitize_sub(subject):
    try:
        return subject.rsplit('_', 1)[1].zfill(2)
    except:
        return subject

def _process_subject(npz_file, output_dir, atlas_labels, lh_path, rh_path, smoke):
    subject = npz_file.stem.replace("all_gradients_", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Processing {subject} ...")
    data = np.load(npz_file, allow_pickle=True)
    gm, labels = data['all_gradients'], data['labels']
    movies = sorted({lbl.rsplit('_', 1)[0] for lbl in labels})
    if smoke:
        movies = movies[:1]
    for movie in movies:
        mask = np.array([lbl.rsplit('_', 1)[0] == movie for lbl in labels])
        _process_movie(subject, movie, gm[mask], labels[mask], output_dir, atlas_labels, lh_path, rh_path, smoke)


def visualize_gradients(source_dir: Path, output_dir: Path, smoke: bool = False):
    print("Setting up atlas...")
    atlas_labels, lh_path, rh_path = _setup_atlas(source_dir / "nilearn")
    output_dir.mkdir(parents=True, exist_ok=True)
    _save_colorbar(output_dir)
    for npz_file in sorted(source_dir.glob("all_gradients_*.npz")):
        _process_subject(npz_file, output_dir, atlas_labels, lh_path, rh_path, smoke)
