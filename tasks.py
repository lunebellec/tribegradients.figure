import shutil
from pathlib import Path
from invoke import task

PROJECT_ROOT = Path(__file__).parent


@task
def fetch(c):
    """
    Download source data archive from Zenodo and extract into source_data/.
    """
    import urllib.request
    import zipfile

    url = "https://zenodo.org/api/records/19924319/files-archive"
    source_dir = PROJECT_ROOT / c.config.get("source_data_dir")
    source_dir.mkdir(parents=True, exist_ok=True)
    archive = source_dir / "archive.zip"

    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, archive)
    print(f"Extracting to {source_dir} ...")
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(source_dir)
    archive.unlink()
    print("Fetch complete.")


@task
def run_visualize_gradients(c, smoke=False):
    """
    Generate gradient brain maps for each participant, movie, and chunk.
    Use --smoke to run a minimal check (average of first movie only).
    """
    from analysis.visualize_gradients import visualize_gradients
    source_dir = PROJECT_ROOT / c.config.get("source_data_dir")
    output_dir = PROJECT_ROOT / c.config.get("output_data_dir") / "gradients"
    visualize_gradients(source_dir, output_dir, smoke=smoke)


@task
def run_visualize_reference_gradients(c, npz_path):
    """
    Generate brain maps for reference gradients from an external NPZ file.
    The NPZ must contain a 'refgradients' array of shape (1000, 4).
    Outputs are saved to source_data/gradients_samara2023/ (not output_data, since
    the raw gradients are not redistributable but the images are).
    """
    from analysis.visualize_gradients import visualize_reference_gradients
    source_dir = PROJECT_ROOT / c.config.get("source_data_dir")
    output_dir = source_dir / "gradients_reference"
    visualize_reference_gradients(Path(npz_path), output_dir, source_dir / "nilearn")


@task
def run_gradient_correlations(c):
    """
    Compute pairwise spatial correlations between gradient maps across comparison types.
    Generates one figure per gradient (1–4) in output_data/gradient_correlations/.
    """
    from analysis.gradient_correlations import gradient_correlations
    source_dir = PROJECT_ROOT / c.config.get("source_data_dir")
    output_dir = PROJECT_ROOT / c.config.get("output_data_dir") / "gradient_correlations"
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
    output_dir = PROJECT_ROOT / c.config.get("output_data_dir") / "gradients"
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
    output_dir = PROJECT_ROOT / c.config.get("output_data_dir") / "gradient_correlations"
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
def dashboard(c, port=8000):
    """
    Serve the project from the root so dashboard/index.html can load images via ../output_data/.
    Open http://localhost:<port>/dashboard/ in your browser.
    """
    import subprocess
    print(f"Serving at http://localhost:{port}/dashboard/")
    subprocess.run(["python", "-m", "http.server", str(port)], cwd=PROJECT_ROOT)


@task
def clean_source(c):
    """
    Remove downloaded source data (*.npz and nilearn/). WARNING: re-run fetch to restore.
    """
    source_dir = PROJECT_ROOT / c.config.get("source_data_dir")
    for npz in source_dir.glob("*.npz"):
        npz.unlink()
        print(f"Removed {npz}")
    nilearn_dir = source_dir / "nilearn"
    if nilearn_dir.exists():
        shutil.rmtree(nilearn_dir)
        print(f"Removed {nilearn_dir}")
