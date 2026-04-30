# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the `airoh-mini` template — a starting point for structuring a reproducible data analysis. It is built on the [`invoke`](https://www.pyinvoke.org/) task runner. The `airoh` pip package provides reusable invoke tasks; this repo customizes them via `tasks.py` and `invoke.yaml`.

## Setup

```bash
# uv (recommended):
uv sync

# pip:
pip install -r requirements.txt

# conda:
conda env create -n airoh_env -f environment.yml && conda activate airoh_env
```

## Common Commands

With `uv`:
```bash
uv run invoke fetch           # Download source data
uv run invoke run             # Full pipeline: run_simulation → run_notebooks
uv run invoke run-simulation  # Generate simulation_output.csv in output_data/
uv run invoke run-notebooks   # Execute notebooks, save figures to output_data/
uv run invoke clean           # Remove *.png and *.csv from output_data/
uv run invoke --list          # Show all available tasks
```

Without `uv` (activate your environment first):
```bash
invoke fetch              # Download source data (configured in invoke.yaml under files:)
invoke run                # Full pipeline: run_simulation → run_notebooks
invoke run-simulation     # Generate simulation_output.csv in output_data/
invoke run-notebooks      # Execute notebooks, save figures to output_data/
invoke clean              # Remove *.png and *.csv from output_data/
invoke --list             # Show all available tasks
```

## Architecture

**Execution flow:** `invoke run` triggers `run_simulation` → `run_notebooks` (declared as `pre=` dependencies in `tasks.py`).

- `invoke.yaml` — all path and data config (`output_data_dir`, `source_data_dir`, `notebooks_dir`, `files:` for downloads)
- `tasks.py` — project-specific invoke tasks; imports reusable tasks from `airoh.utils`
- `analysis/simulation.py` — pure Python analysis logic; called by `run_simulation` task
- `notebooks/` — Jupyter notebooks executed by `run_notebooks` via `airoh.utils.run_notebooks`; notebooks receive `OUTPUT_DATA_DIR` and `SOURCE_DATA_DIR` as environment variables
- `source_data/` and `output_data/` — excluded from Git by `.gitignore`

**Adding a new analysis step:** add a function to `analysis/`, create or extend a notebook in `notebooks/`, add an invoke task in `tasks.py`, and wire it into the `pre=` chain on `run`.
