import shutil
from pathlib import Path
from invoke import task


@task
def fetch(c):
    """
    Retrieve all data assets.
    """
    pass


@task
def run_visualize_gradients(c, smoke=False):
    """
    Generate gradient brain maps for each participant, movie, and chunk.
    Use --smoke to run a minimal check (average of first movie only).
    """
    from analysis.visualize_gradients import visualize_gradients
    source_dir = Path(c.config.get("source_data_dir"))
    output_dir = Path(c.config.get("output_data_dir")) / "gradients"
    visualize_gradients(source_dir, output_dir, smoke=smoke)


@task
def run_gradient_correlations(c):
    """
    Compute pairwise spatial correlations between gradient maps across comparison types.
    Generates one figure per gradient (1–4) in output_data/gradient_correlations/.
    """
    from analysis.gradient_correlations import gradient_correlations
    source_dir = Path(c.config.get("source_data_dir"))
    output_dir = Path(c.config.get("output_data_dir")) / "gradient_correlations"
    gradient_correlations(source_dir, output_dir)


@task(pre=[run_visualize_gradients, run_gradient_correlations])
def run(c):
    """
    Run the full analysis pipeline.
    """
    print("All analyses completed.")


@task
def clean_visualize_gradients(c):
    """
    Remove all gradient visualization output so the task can be re-run from scratch.
    """
    output_dir = Path(c.config.get("output_data_dir")) / "gradients"
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"Removed {output_dir}")
    else:
        print(f"Nothing to clean: {output_dir} does not exist")


@task
def clean_gradient_correlations(c):
    """
    Remove all gradient correlations output so the task can be re-run from scratch.
    """
    output_dir = Path(c.config.get("output_data_dir")) / "gradient_correlations"
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"Removed {output_dir}")
    else:
        print(f"Nothing to clean: {output_dir} does not exist")


@task(pre=[clean_visualize_gradients, clean_gradient_correlations])
def clean(c):
    """
    Clean all analysis outputs (does NOT touch source_data).
    """
    print("All outputs cleaned.")


@task
def clean_source(c):
    """
    Remove downloaded source data (*.npz and nilearn/). WARNING: re-run fetch to restore.
    """
    source_dir = Path(c.config.get("source_data_dir"))
    for npz in source_dir.glob("*.npz"):
        npz.unlink()
        print(f"Removed {npz}")
    nilearn_dir = source_dir / "nilearn"
    if nilearn_dir.exists():
        shutil.rmtree(nilearn_dir)
        print(f"Removed {nilearn_dir}")
