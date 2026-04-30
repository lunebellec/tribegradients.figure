# tribe_gradients.figure

Visualizes functional connectivity gradients computed from fMRI data recorded while subjects watched naturalistic movie stimuli (TRIBE dataset).

## Setup

```bash
uv sync
```

## Usage

```bash
uv run invoke fetch                    # Download source data
uv run invoke run                      # Full analysis pipeline
uv run invoke run-visualize-gradients  # Generate gradient brain maps in output_data/gradients/
uv run invoke clean                    # Remove *.png from output_data/
uv run invoke --list                   # Show all available tasks
```

## Data

See [source_data/CONTENT.md](source_data/CONTENT.md) for source data documentation and [output_data/CONTENT.md](output_data/CONTENT.md) for output documentation.
