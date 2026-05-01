# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Reproducible figure pipeline for visualizing functional connectivity gradients from the TRIBE fMRI dataset. Built on the [`invoke`](https://www.pyinvoke.org/) task runner with the `airoh` package providing reusable tasks.

## Setup

```bash
uv sync
```

## Common Commands

```bash
uv run invoke fetch                    # Download source data
uv run invoke run                      # Full pipeline
uv run invoke run-visualize-gradients  # Generate gradient brain maps in output_data/gradients/
uv run invoke clean                    # Remove *.png from output_data/
uv run invoke --list                   # Show all available tasks
```

## Architecture

- `invoke.yaml` — path config (`output_data_dir`, `source_data_dir`)
- `tasks.py` — invoke tasks; `run` chains all analysis steps via `pre=`
- `analysis/visualize_gradients.py` — projects Schaefer atlas to surface once, then maps gradient values per-vertex for each subject/movie/chunk
- `source_data/` and `output_data/` — excluded from Git by `.gitignore`

**Adding a new analysis step:** add a function to `analysis/`, add an invoke task in `tasks.py`, and wire it into `pre=` on `run`.
