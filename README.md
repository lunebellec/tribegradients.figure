# Airoh Template: Reproducible Pipelines Made Simple

_why don't you have a cup of relaxing jasmine tea?_

This repository is a template for structuring a reproducible data analysis. Built on the [`invoke`](https://www.pyinvoke.org/) task runner, it lets you go from clean clone to output figures with just a few commands.

The logic is powered by [`airoh`](https://pypi.org/project/airoh/), a lightweight, pip-installable Python package of reusable `invoke` tasks. This repository runs small analyses just to demonstrate how the `airoh-template` works. It should be easy to adapt to a variety of other projects.

⚠️ **Status**: This template is in its early days. Expect rapid iteration and changes.

---

## ✨ TL;DR:

This repository is a [GitHub template](https://github.com/airoh-pipeline/airoh-template/generate). Click **”Use this template”** to create your own analysis project.
```bash
uv sync
uv run invoke fetch
uv run invoke run
```
Voilà — from clone to full reproduction.

---

## 🚀 Quick Start

### **Step 1**: Install dependencies

Using `uv` (recommended):
```bash
uv sync
```
This creates a `.venv` and installs all dependencies from `pyproject.toml`.

Using `pip` (e.g. in a virtual environment):
```bash
pip install -r requirements.txt
```

Using `conda`:
```bash
conda env create -n airoh_env -f environment.yml
conda activate airoh_env
```

---


---
### **Step 2**: Fetch the source data

```
bash
invoke fetch
```

This downloads the configured file(s) listed under `files:` in `invoke.yaml`.

---

### **Step 3**: Run the analysis pipeline

```
bash
invoke run
```

This will execute a full analysis pipeline (simulation + figures).

---

### **Step 4**: Clean output data

```
bash
invoke clean
```

Removes the output folder listed in `invoke.yaml` under `output_data_dir`.

---

## 🧠 Core Features

* Modular `tasks.py` that imports reusable code from `airoh`
* Minimal and readable `invoke.yaml` configuration file
* Real output notebooks & figures — ready to publish

---

## 🧰 Task Overview

| Task    | Description                                                 |
| ------- | ----------------------------------------------------------- |
| `fetch` | Downloads dataset using config in `invoke.yaml` |
| `run`   | Executes Jupyter notebooks for each figure                  |
| `clean` | Removes the `output_data_dir` contents                      |

Use `invoke --list` or `invoke --help <task>` for descriptions and usage.

---

## 🧭 Tips

* Use `invoke --complete` for tab-completion support
* Configure paths and data sources in `invoke.yaml`
* To use this template for a new project, start from [`airoh-template`](https://github.com/SIMEXP/airoh-template) and customize `tasks.py` + `invoke.yaml`

---

## 📁 Folder Structure

| Folder         | Description                              |
| -------------- | ---------------------------------------- |
| `notebooks/`   | Jupyter notebooks (e.g., one per figure) |
| `source_data/` | Raw source datasets                      |
| `output_data/` | Generated results and figures            |
| `tasks.py`     | Project-specific invoke entrypoint       |
| `invoke.yaml`  | Config file for all reusable tasks       |

---

## 🔁 Want to contribute?

Submit an issue or PR on [`airoh`](https://github.com/SIMEXP/airoh).

---

## Philosophy

Inspired by Uncle Iroh from *Avatar: The Last Airbender*, `airoh` aims to bring simplicity, reusability, and clarity to research infrastructure — one well-structured task at a time.
