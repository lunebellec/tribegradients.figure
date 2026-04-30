from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from nilearn.datasets import fetch_atlas_schaefer_2018, load_fsaverage
from nilearn.plotting import plot_surf_stat_map
from nilearn.surface import SurfaceImage


def _setup_atlas(data_dir: Path):
    schaefer_atlas = fetch_atlas_schaefer_2018(n_rois=1000, yeo_networks=7, data_dir=data_dir)
    fsaverage = load_fsaverage(data_dir=data_dir)
    atlas_surf = SurfaceImage.from_volume(mesh=fsaverage["pial"], volume_img=schaefer_atlas['maps'])
    left_labels = np.round(atlas_surf.data.parts['left']).astype(int)
    right_labels = np.round(atlas_surf.data.parts['right']).astype(int)
    return (left_labels, right_labels), fsaverage


def _grad_to_surf(grad_values, left_labels, right_labels, fsaverage):
    def _map(labels):
        out = np.zeros(len(labels))
        mask = labels > 0
        out[mask] = grad_values[labels[mask] - 1]
        return out
    return SurfaceImage(
        mesh=fsaverage["pial"],
        data={'left': _map(left_labels), 'right': _map(right_labels)},
    )


def _save_gradient_map(gradients, title, path, atlas_labels, fsaverage, cmap="viridis_r"):
    left_labels, right_labels = atlas_labels
    fig, ax = plt.subplots(4, 4, figsize=(10, 10), subplot_kw={'projection': '3d'})
    for i in range(min(4, gradients.shape[1])):
        cur_surf = _grad_to_surf(gradients[:, i], left_labels, right_labels, fsaverage)
        common = dict(threshold=None, colorbar=False, cmap=cmap, figure=fig)
        plot_surf_stat_map(stat_map=cur_surf, view="lateral", hemi='left',  axes=ax[i, 0], **common)
        plot_surf_stat_map(stat_map=cur_surf, view="medial",  hemi='left',  axes=ax[i, 1], **common)
        plot_surf_stat_map(stat_map=cur_surf, view="lateral", hemi='right', axes=ax[i, 2], **common)
        plot_surf_stat_map(stat_map=cur_surf, view="medial",  hemi='right', axes=ax[i, 3], **common)

    plt.suptitle(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def visualize_gradients(source_dir: Path, output_dir: Path):
    atlas_labels, fsaverage = _setup_atlas(source_dir / "nilearn")

    for npz_file in sorted(source_dir.glob("all_gradients_*.npz")):
        subject = npz_file.stem.replace("all_gradients_", "")
        print(f"Processing {subject} ...")
        data = np.load(npz_file, allow_pickle=True)
        gm = data['all_gradients']  # (n_runs, 1000, 4)
        labels = data['labels']      # (n_runs,)

        subj_dir = output_dir / subject
        movies = sorted({lbl.rsplit('_', 1)[0] for lbl in labels})

        for movie in movies:
            mask = np.array([lbl.rsplit('_', 1)[0] == movie for lbl in labels])
            movie_gm = gm[mask]           # (n_chunks, 1000, 4)
            movie_labels = labels[mask]

            _save_gradient_map(
                movie_gm.mean(axis=0),
                f"{subject} — {movie} (average)",
                subj_dir / f"{movie}_average.png",
                atlas_labels, fsaverage,
            )
            print(f"  {movie}: average saved")

            for chunk_gm, label in zip(movie_gm, movie_labels):
                _save_gradient_map(
                    chunk_gm,
                    f"{subject} — {label}",
                    subj_dir / f"{label}.png",
                    atlas_labels, fsaverage,
                )
            print(f"  {movie}: {len(movie_labels)} chunks saved")
