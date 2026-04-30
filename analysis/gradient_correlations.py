from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def _load_data(source_dir):
    human, tribe = {}, None
    for npz in sorted(source_dir.glob("all_gradients_*.npz")):
        d = np.load(npz, allow_pickle=True)
        key = npz.stem.replace("all_gradients_", "")
        if key == "tribe":
            tribe = {"gradients": d["all_gradients"], "labels": d["labels"]}
        else:
            human[key] = {"gradients": d["all_gradients"], "labels": d["labels"]}
    return human, tribe


def _flatten_entries(data_dict, is_tribe=False):
    """Return list of dicts with keys: subject, movie, vec_idx (row in original array), array ref."""
    entries = []
    for subject, d in data_dict.items():
        for i, label in enumerate(d["labels"]):
            movie = label.rsplit("_", 1)[0]
            entries.append({"subject": subject, "movie": movie, "row": i, "data": d})
    return entries


def _get_vecs(entries, gradient_idx):
    return np.array([e["data"]["gradients"][e["row"], :, gradient_idx] for e in entries])


def _pearsonr_rows(X):
    """All pairwise Pearson r within rows of X. Returns (n, n) matrix."""
    Xc = X - X.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(Xc, axis=1, keepdims=True)
    norm[norm == 0] = 1
    Xn = Xc / norm
    return Xn @ Xn.T


def _pearsonr_cross(X, Y):
    """Pearson r between every row of X and every row of Y. Returns (n, m) matrix."""
    Xc = X - X.mean(axis=1, keepdims=True)
    Yc = Y - Y.mean(axis=1, keepdims=True)
    Xn_norm = np.linalg.norm(Xc, axis=1, keepdims=True)
    Yn_norm = np.linalg.norm(Yc, axis=1, keepdims=True)
    Xn_norm[Xn_norm == 0] = 1
    Yn_norm[Yn_norm == 0] = 1
    return (Xc / Xn_norm) @ (Yc / Yn_norm).T



def _compute_correlations(human_data, tribe_data, gradient_idx):
    h_entries = _flatten_entries(human_data)
    t_entries = _flatten_entries({"tribe": tribe_data})

    h_vecs = _get_vecs(h_entries, gradient_idx)   # (n_h, 1000)
    t_vecs = _get_vecs(t_entries, gradient_idx)   # (n_t, 1000)

    h_subj = np.array([e["subject"] for e in h_entries])
    h_movie = np.array([e["movie"] for e in h_entries])
    t_movie = np.array([e["movie"] for e in t_entries])

    hh = _pearsonr_rows(h_vecs)  # (n_h, n_h)
    ht = _pearsonr_cross(h_vecs, t_vecs)  # (n_h, n_t)

    i_idx, j_idx = np.triu_indices(len(h_entries), k=1)

    same_subj = h_subj[i_idx] == h_subj[j_idx]
    same_movie_hh = h_movie[i_idx] == h_movie[j_idx]

    categories = {}

    # Within-subject group first, then across-subjects group
    categories["Within movie\nwithin subject"] = hh[i_idx[same_subj & same_movie_hh],
                                                     j_idx[same_subj & same_movie_hh]]
    categories["Between movies\nwithin subject"] = hh[i_idx[same_subj & ~same_movie_hh],
                                                      j_idx[same_subj & ~same_movie_hh]]
    categories["Within movie\nbetween subjects"] = hh[i_idx[~same_subj & same_movie_hh],
                                                      j_idx[~same_subj & same_movie_hh]]
    categories["Between movies\nbetween subjects"] = hh[i_idx[~same_subj & ~same_movie_hh],
                                                        j_idx[~same_subj & ~same_movie_hh]]

    same_movie_ht = h_movie[:, None] == t_movie[None, :]  # (n_h, n_t)
    categories["Tribe vs human\nwithin movie"] = ht[same_movie_ht]
    categories["Tribe vs human\nbetween movies"] = ht[~same_movie_ht]

    avg_h = h_vecs.mean(axis=0, keepdims=True)
    avg_t = t_vecs.mean(axis=0, keepdims=True)

    categories["Average human gradient\nvs human"] = _pearsonr_cross(avg_h, h_vecs)[0]
    categories["Average tribe gradient\nvs tribe"] = _pearsonr_cross(avg_t, t_vecs)[0]
    categories["Average human gradient\nvs tribe"] = _pearsonr_cross(avg_h, t_vecs)[0]
    categories["Average tribe gradient\nvs human"] = _pearsonr_cross(avg_t, h_vecs)[0]

    return categories


_COLORS = {
    "Within movie\nwithin subject":     "#555555",
    "Between movies\nwithin subject":   "#555555",
    "Within movie\nbetween subjects":   "#555555",
    "Between movies\nbetween subjects": "#555555",
    "Tribe vs human\nwithin movie":     "#E07B2A",
    "Tribe vs human\nbetween movies":   "#E07B2A",
    "Average human gradient\nvs human":  "#2D7BB5",
    "Average tribe gradient\nvs tribe":  "#2D7BB5",
    "Average human gradient\nvs tribe":  "#7B3FA0",
    "Average tribe gradient\nvs human":  "#7B3FA0",
}

# Section separators (between which y positions)
_SEPARATORS = [1.5, 3.5, 5.5]


def _draw_distribution(ax, vals, y, color, box_height=0.45):
    p5, q1, median, q3, p95 = np.percentile(vals, [5, 25, 50, 75, 95])
    mean = np.mean(vals)

    # 5th–95th percentile whisker
    ax.plot([p5, p95], [y, y], color=color, linewidth=1.2, alpha=0.5, solid_capstyle="round")

    # IQR box
    box = plt.Rectangle((q1, y - box_height / 2), q3 - q1, box_height,
                         facecolor=color, alpha=0.25, edgecolor=color, linewidth=1.2)
    ax.add_patch(box)

    # Median tick
    ax.plot([median, median], [y - box_height / 2, y + box_height / 2],
            color=color, linewidth=1.8, solid_capstyle="butt")

    # Mean dot (highlighted)
    ax.plot(mean, y, "o", color=color, markersize=7, zorder=5,
            markeredgecolor="white", markeredgewidth=1.0)


def _plot_gradient(categories, gradient_idx, output_path):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    labels = list(categories.keys())
    y_pos = np.arange(len(labels))

    for y, label in zip(y_pos, labels):
        _draw_distribution(ax, categories[label], y, _COLORS[label])

    for sep in _SEPARATORS:
        ax.axhline(sep, color="lightgray", linewidth=0.8, linestyle="--")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Pearson r", fontsize=10)
    ax.set_title(f"Gradient {gradient_idx + 1} — Spatial Correlations", fontsize=11, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", color="lightgray", linewidth=0.8)

    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor="#555555", alpha=0.25, edgecolor="#555555", label="Human–Human"),
        Patch(facecolor="#E07B2A", alpha=0.25, edgecolor="#E07B2A", label="Tribe vs Human"),
        Patch(facecolor="#2D7BB5", alpha=0.25, edgecolor="#2D7BB5", label="Average gradient vs self"),
        Patch(facecolor="#7B3FA0", alpha=0.25, edgecolor="#7B3FA0", label="Average gradient vs other"),
        Line2D([0], [0], marker="o", color="gray", linestyle="None", markersize=6,
               markeredgecolor="white", label="Mean"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="upper left", framealpha=0.85)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {output_path}")


def gradient_correlations(source_dir: Path, output_dir: Path):
    print("Loading gradient data...")
    human_data, tribe_data = _load_data(source_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for grad_idx in range(4):
        print(f"Computing correlations for gradient {grad_idx + 1}...")
        categories = _compute_correlations(human_data, tribe_data, grad_idx)
        out_path = output_dir / f"gradient_{grad_idx + 1}_correlations.pdf"
        _plot_gradient(categories, grad_idx, out_path)

    print("Done.")
