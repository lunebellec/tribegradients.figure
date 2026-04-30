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


@task(pre=[run_visualize_gradients])
def run(c):
    """
    Run the full analysis pipeline.
    """
    print("All analyses completed.")


@task
def clean(c):
    """
    Clean the output folder.
    """
    from airoh.utils import clean_folder
    clean_folder(c, "output_data_dir", "*.png")


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
