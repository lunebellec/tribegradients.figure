from pathlib import Path
from invoke import task


@task
def fetch(c):
    """
    Retrieve all data assets.
    """
    pass


@task
def run_visualize_gradients(c):
    """
    Generate gradient brain maps for each participant, movie, and chunk.
    """
    from analysis.visualize_gradients import visualize_gradients
    source_dir = Path(c.config.get("source_data_dir"))
    output_dir = Path(c.config.get("output_data_dir")) / "gradients"
    visualize_gradients(source_dir, output_dir)


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
