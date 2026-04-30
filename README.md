# tribe_gradients.figure

Visualizes functional connectivity gradients computed from fMRI data recorded while subjects watched naturalistic movie stimuli (TRIBE dataset).

## Setup

```bash
uv sync
```

## Usage

Pre-generated outputs are committed to this repository. To reproduce the figures from scratch:

```bash
uv run invoke clean                    # Remove committed outputs from output_data/
uv run invoke fetch                    # Download source data from Zenodo
uv run invoke run                      # Full analysis pipeline
uv run invoke --list                   # Show all available tasks
```

To browse the outputs interactively:

```bash
uv run invoke dashboard                # Serve dashboard at http://localhost:8000/dashboard/
```

## Data

See [source_data/CONTENT.md](source_data/CONTENT.md) for source data documentation and [output_data/CONTENT.md](output_data/CONTENT.md) for output documentation.
