from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from nilearn.datasets import fetch_atlas_schaefer_2018, load_fsaverage
from nilearn.image import iter_img
from nilearn.maskers import NiftiLabelsMasker
from nilearn.plotting import plot_surf_stat_map
from nilearn.surface import SurfaceImage


def _setup_atlas(data_dir: Path):
    schaefer_atlas = fetch_atlas_schaefer_2018(n_rois=1000, yeo_networks=7, data_dir=data_dir)
    masker = NiftiLabelsMasker(
        labels_img=schaefer_atlas['maps'], standardize=True, memory='nilearn_cache'
    )
    masker.fit()
    return masker, load_fsaverage(data_dir=data_dir)


def _save_gradient_map(gradients, title, path, masker, fsaverage, cmap="viridis_r"):
    """Save a 4×4 surface figure (4 gradients × left/right × lateral/medial views)."""
    # gradients: (1000, 4) — inverse_transform expects (n_samples, n_features)
    img = masker.inverse_transform(gradients.T)  # (4, 1000) → 4D NIfTI (x,y,z,4)

    fig, ax = plt.subplots(4, 4, figsize=(10, 10), subplot_kw={'projection': '3d'})
    for i, cur_nii in enumerate(iter_img(img)):
        if i == 4:
            break
        cur_surf = SurfaceImage.from_volume(mesh=fsaverage["pial"], volume_img=cur_nii)
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
    masker, fsaverage = _setup_atlas(source_dir / "nilearn")

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
                masker, fsaverage,
            )
            print(f"  {movie}: average saved")

            for chunk_gm, label in zip(movie_gm, movie_labels):
                _save_gradient_map(
                    chunk_gm,
                    f"{subject} — {label}",
                    subj_dir / f"{label}.png",
                    masker, fsaverage,
                )
            print(f"  {movie}: {len(movie_labels)} chunks saved")
