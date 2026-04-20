"""
data_loader.py — Dataset loading and preprocessing for The Audit lab.

Provides a consistent DataLoader interface for both the HAM10000 test split
and the African-context stress-test dataset. Both datasets use identical
transforms so results are directly comparable.
"""

import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# ---------------------------------------------------------------------------
# ImageNet normalisation constants
# ---------------------------------------------------------------------------
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Class abbreviations used consistently throughout the lab
CLASS_NAMES = ["nv", "mel", "bcc", "akiec", "bkl", "df", "vasc"]

# Fitzpatrick type labels for display
FITZPATRICK_LABELS = {
    1: "Type I",
    2: "Type II",
    3: "Type III",
    4: "Type IV",
    5: "Type V",
    6: "Type VI",
}

# ---------------------------------------------------------------------------
# Shared transform pipeline — identical for both datasets
# ---------------------------------------------------------------------------
AUDIT_TRANSFORM = transforms.Compose(
    [
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ]
)


# ---------------------------------------------------------------------------
# Dataset classes
# ---------------------------------------------------------------------------


class HAM10000TestDataset(Dataset):
    """PyTorch Dataset for the HAM10000 held-out test split.

    Args:
        data_dir: Path to the directory containing HAM10000 test images.
        metadata_path: Path to HAM10000_metadata.csv.
        transform: Torchvision transforms to apply. Defaults to AUDIT_TRANSFORM.
    """

    def __init__(
        self,
        data_dir: str,
        metadata_path: str,
        transform: Optional[transforms.Compose] = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.transform = transform or AUDIT_TRANSFORM

        df = pd.read_csv(metadata_path)
        # Keep only images that exist on disk
        df["image_path"] = df["image_id"].apply(
            lambda x: self.data_dir / f"{x}.jpg"
        )
        df = df[df["image_path"].apply(lambda p: p.exists())].reset_index(drop=True)

        self.metadata = df
        self.image_ids = df["image_id"].tolist()
        self.labels = [CLASS_NAMES.index(dx) for dx in df["dx"].tolist()]

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int):
        row = self.metadata.iloc[idx]
        image = Image.open(row["image_path"]).convert("RGB")
        label = self.labels[idx]
        image_id = self.image_ids[idx]

        if self.transform:
            image = self.transform(image)

        return image, label, image_id


class AfricanContextDataset(Dataset):
    """PyTorch Dataset for the African-context stress-test images.

    Structurally identical to HAM10000TestDataset for drop-in compatibility.
    Images are consumer phone photos (not dermatoscope) collected in West Africa.

    Args:
        data_dir: Path to the directory containing African-context images.
        labels_path: Path to african_context_labels.csv.
        transform: Torchvision transforms to apply. Defaults to AUDIT_TRANSFORM.
    """

    def __init__(
        self,
        data_dir: str,
        labels_path: str,
        transform: Optional[transforms.Compose] = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.transform = transform or AUDIT_TRANSFORM

        df = pd.read_csv(labels_path)
        df["image_path"] = df["image_id"].apply(
            lambda x: self.data_dir / f"{x}.jpg"
        )
        df = df[df["image_path"].apply(lambda p: p.exists())].reset_index(drop=True)

        self.metadata = df
        self.image_ids = df["image_id"].tolist()
        self.labels = [CLASS_NAMES.index(dx) for dx in df["dx"].tolist()]

        # Fitzpatrick type is available for this dataset (not for HAM10000)
        self.fitzpatrick_types = (
            df["fitzpatrick_type"].tolist()
            if "fitzpatrick_type" in df.columns
            else [None] * len(df)
        )

    def __len__(self) -> int:
        return len(self.metadata)

    def __getitem__(self, idx: int):
        row = self.metadata.iloc[idx]
        image = Image.open(row["image_path"]).convert("RGB")
        label = self.labels[idx]
        image_id = self.image_ids[idx]

        if self.transform:
            image = self.transform(image)

        return image, label, image_id


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def get_dataloader(
    dataset_name: str,
    batch_size: int = 32,
    shuffle: bool = False,
    data_dir: str = "data",
    num_workers: int = 2,
) -> DataLoader:
    """Returns a DataLoader for the specified dataset.

    Both datasets use identical transforms so their outputs are directly
    comparable — same input space, same normalisation, same spatial crop.

    Args:
        dataset_name: One of 'ham10000_test' or 'african_context'.
        batch_size: Number of samples per batch.
        shuffle: Whether to shuffle the dataset. Set False for evaluation.
        data_dir: Root data directory. Should contain subdirectories for each
            dataset and their respective CSV label files.
        num_workers: Number of parallel DataLoader workers.

    Returns:
        A configured PyTorch DataLoader.

    Raises:
        ValueError: If dataset_name is not recognised.
        FileNotFoundError: If required data files are not found under data_dir.
    """
    data_root = Path(data_dir)

    if dataset_name == "ham10000_test":
        images_dir = data_root / "ham10000_test" / "images"
        metadata_path = data_root / "ham10000_test" / "HAM10000_metadata.csv"

        if not images_dir.exists():
            raise FileNotFoundError(
                f"HAM10000 test images not found at {images_dir}. "
                "See data/README.md for download instructions."
            )
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"HAM10000 metadata not found at {metadata_path}."
            )

        dataset = HAM10000TestDataset(
            data_dir=str(images_dir),
            metadata_path=str(metadata_path),
        )

    elif dataset_name == "african_context":
        images_dir = data_root / "african_context" / "images"
        labels_path = data_root / "african_context" / "african_context_labels.csv"

        if not images_dir.exists():
            raise FileNotFoundError(
                f"African-context images not found at {images_dir}. "
                "Run the dataset download cell in ACT 1."
            )
        if not labels_path.exists():
            raise FileNotFoundError(
                f"African-context labels not found at {labels_path}."
            )

        dataset = AfricanContextDataset(
            data_dir=str(images_dir),
            labels_path=str(labels_path),
        )

    else:
        raise ValueError(
            f"Unknown dataset '{dataset_name}'. "
            "Valid options: 'ham10000_test', 'african_context'."
        )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True,
    )


def get_dataset_info(dataset_name: str, data_dir: str = "data") -> dict:
    """Returns metadata about a dataset without loading all images.

    Args:
        dataset_name: One of 'ham10000_test' or 'african_context'.
        data_dir: Root data directory.

    Returns:
        A dict with keys:
            num_samples (int): Total number of images.
            class_distribution (dict): Class abbreviation -> count.
            fitzpatrick_distribution (dict | None): Fitzpatrick type -> count,
                or None if not available for this dataset.

    Raises:
        ValueError: If dataset_name is not recognised.
        FileNotFoundError: If the CSV label file is not found.
    """
    data_root = Path(data_dir)

    if dataset_name == "ham10000_test":
        metadata_path = data_root / "ham10000_test" / "HAM10000_metadata.csv"
        if not metadata_path.exists():
            raise FileNotFoundError(str(metadata_path))
        df = pd.read_csv(metadata_path)
        fitzpatrick_dist = None  # Not systematically recorded in HAM10000

    elif dataset_name == "african_context":
        labels_path = data_root / "african_context" / "african_context_labels.csv"
        if not labels_path.exists():
            raise FileNotFoundError(str(labels_path))
        df = pd.read_csv(labels_path)
        fitzpatrick_dist = (
            df["fitzpatrick_type"].value_counts().to_dict()
            if "fitzpatrick_type" in df.columns
            else None
        )

    else:
        raise ValueError(
            f"Unknown dataset '{dataset_name}'. "
            "Valid options: 'ham10000_test', 'african_context'."
        )

    class_dist = df["dx"].value_counts().to_dict()

    return {
        "num_samples": len(df),
        "class_distribution": class_dist,
        "fitzpatrick_distribution": fitzpatrick_dist,
    }
