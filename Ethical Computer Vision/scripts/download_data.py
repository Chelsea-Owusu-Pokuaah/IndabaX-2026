"""
download_data.py — Script to download and verify datasets for The Audit lab.

Usage:
    python scripts/download_data.py --dataset ham10000 --data-dir data/
    python scripts/download_data.py --dataset african_context --drive-id FILE_ID

Requires:
    kaggle CLI (for ham10000): pip install kaggle
    gdown (for african_context): pip install gdown
"""

import argparse
import hashlib
import os
import shutil
import zipfile
from pathlib import Path


def download_ham10000(data_dir: str) -> None:
    """Downloads the HAM10000 dataset from Kaggle using the Kaggle CLI.

    Requires the Kaggle API key to be configured at ~/.kaggle/kaggle.json
    or via KAGGLE_USERNAME / KAGGLE_KEY environment variables.

    Args:
        data_dir: Root data directory. Dataset will be placed at
            data_dir/ham10000_test/.
    """
    try:
        import kaggle  # noqa: F401
    except ImportError:
        print(
            "ERROR: kaggle package not found.\n"
            "Install it with: pip install kaggle\n"
            "Then configure your API key at: https://www.kaggle.com/docs/api"
        )
        return

    target_dir = Path(data_dir) / "ham10000_test"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading HAM10000 from Kaggle to {target_dir} ...")
    os.system(
        f"kaggle datasets download -d kmader/skin-lesion-analysis-toward-melanoma-detection "
        f"-p {target_dir} --unzip"
    )

    # Verify expected files are present
    metadata_path = target_dir / "HAM10000_metadata.csv"
    if not metadata_path.exists():
        print(
            "WARNING: HAM10000_metadata.csv not found after download.\n"
            "Manually place the CSV file at: " + str(metadata_path)
        )
    else:
        print(f"Found metadata at {metadata_path}")

    images_dir = target_dir / "images"
    images_dir.mkdir(exist_ok=True)
    n_images = len(list(images_dir.glob("*.jpg")))
    print(f"Images found: {n_images} (expected ~2,000 for the test split)")


def download_african_context(data_dir: str, drive_id: str) -> None:
    """Downloads the African-context dataset ZIP from Google Drive.

    Args:
        data_dir: Root data directory. Dataset will be extracted to
            data_dir/african_context/.
        drive_id: Google Drive file ID of african_context_dataset.zip.
    """
    try:
        import gdown
    except ImportError:
        print(
            "ERROR: gdown not found.\n"
            "Install it with: pip install gdown"
        )
        return

    target_dir = Path(data_dir) / "african_context"
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / "african_context_dataset.zip"

    print(f"Downloading African-context dataset from Google Drive ...")
    url = f"https://drive.google.com/uc?id={drive_id}"
    gdown.download(url, str(zip_path), quiet=False)

    if not zip_path.exists():
        print("ERROR: Download failed. Check the Drive file ID and permissions.")
        return

    print(f"Extracting {zip_path} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    zip_path.unlink()  # Remove ZIP after extraction

    # Verify
    labels_path = target_dir / "african_context_labels.csv"
    images_dir = target_dir / "images"

    if not labels_path.exists():
        print(f"WARNING: {labels_path} not found after extraction.")
    else:
        print(f"Labels file found: {labels_path}")

    if not images_dir.exists():
        print(f"WARNING: {images_dir} directory not found after extraction.")
    else:
        n_images = len(list(images_dir.glob("*.jpg")))
        print(f"Images found: {n_images} (expected 60–80)")


def verify_dataset(data_dir: str, dataset_name: str) -> None:
    """Checks that a dataset is correctly placed and counts files.

    Args:
        data_dir: Root data directory.
        dataset_name: One of 'ham10000_test' or 'african_context'.
    """
    data_root = Path(data_dir)

    if dataset_name == "ham10000_test":
        images_dir = data_root / "ham10000_test" / "images"
        metadata = data_root / "ham10000_test" / "HAM10000_metadata.csv"
    elif dataset_name == "african_context":
        images_dir = data_root / "african_context" / "images"
        metadata = data_root / "african_context" / "african_context_labels.csv"
    else:
        print(f"Unknown dataset: {dataset_name}")
        return

    print(f"\n=== Verifying {dataset_name} ===")
    print(f"  Images dir : {images_dir} — {'EXISTS' if images_dir.exists() else 'MISSING'}")
    print(f"  Labels CSV : {metadata} — {'EXISTS' if metadata.exists() else 'MISSING'}")
    if images_dir.exists():
        n = len(list(images_dir.glob("*.jpg")))
        print(f"  Image count: {n}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and verify datasets for The Audit lab."
    )
    parser.add_argument(
        "--dataset",
        choices=["ham10000", "african_context", "verify"],
        required=True,
        help="Which dataset to download, or 'verify' to check existing files.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Root data directory (default: data/)",
    )
    parser.add_argument(
        "--drive-id",
        default=None,
        help="Google Drive file ID for african_context dataset ZIP.",
    )

    args = parser.parse_args()

    if args.dataset == "ham10000":
        download_ham10000(args.data_dir)
        verify_dataset(args.data_dir, "ham10000_test")

    elif args.dataset == "african_context":
        if not args.drive_id:
            print("ERROR: --drive-id is required for african_context download.")
            return
        download_african_context(args.data_dir, args.drive_id)
        verify_dataset(args.data_dir, "african_context")

    elif args.dataset == "verify":
        verify_dataset(args.data_dir, "ham10000_test")
        verify_dataset(args.data_dir, "african_context")


if __name__ == "__main__":
    main()
