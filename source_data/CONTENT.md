# Source Data

Five `.npz` files containing functional connectivity gradients computed from fMRI data recorded while subjects watched naturalistic movie stimuli.

## Files

| File | Runs | Description |
|------|------|-------------|
| `all_gradients_subject_1.npz` | 61 | Individual subject 1 |
| `all_gradients_subject_2.npz` | 61 | Individual subject 2 |
| `all_gradients_subject_3.npz` | 61 | Individual subject 3 |
| `all_gradients_subject_5.npz` | 61 | Individual subject 5 |
| `all_gradients_tribe.npz`     | 44 | Tribe group          |

## Arrays (per file)

Each `.npz` file contains three arrays:

### `all_gradients` — shape `(n_runs, 1000, 4)`, float64

Functional connectivity gradients for each run. The 1000 parcels correspond to the [Schaefer 2018 atlas](https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal) (1000 ROIs, 7 Yeo networks). The 4 values per parcel are the scores along the first 4 principal gradients of functional connectivity.

### `labels` — shape `(n_runs,)`, string

Run identifiers in the format `{movie}_{chunk_index}`. Each label maps a run to a specific temporal chunk of a movie. Four movies are present:

| Label prefix | Movie | Chunks (subjects) | Chunks (tribe) |
|---|---|---|---|
| `bourne`  | The Bourne Identity        | 10 | 10 |
| `figures` | Hidden Figures             | 24 | 12 |
| `life`    | Life (BBC documentary)     | 10 |  5 |
| `wolf`    | The Wolf of Wall Street    | 17 | 17 |

### `eigenvalues` — shape `(n_runs, 4)`, float32

Explained variance (eigenvalues) associated with each of the 4 gradients for every run. Can be used to weight or normalize gradient scores across runs.
