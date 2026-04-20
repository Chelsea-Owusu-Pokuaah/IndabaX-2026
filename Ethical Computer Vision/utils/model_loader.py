"""
model_loader.py — Model loading and inference wrappers for The Audit lab.

Handles loading the EfficientNet-B0 checkpoint and running inference over
a DataLoader or a single PIL image.
"""

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from tqdm import tqdm

try:
    import timm
except ImportError as e:
    raise ImportError(
        "timm is required. Run the setup cell to install dependencies."
    ) from e

from utils.data_loader import AUDIT_TRANSFORM

# Canonical class ordering — index corresponds to model output index
CLASS_NAMES = ["nv", "mel", "bcc", "akiec", "bkl", "df", "vasc"]
CLASS_LABELS = {
    "nv": "Melanocytic Nevi",
    "mel": "Melanoma",
    "bcc": "Basal Cell Carcinoma",
    "akiec": "Actinic Keratoses",
    "bkl": "Benign Keratoses",
    "df": "Dermatofibroma",
    "vasc": "Vascular Lesions",
}


def load_audit_model(
    model_path: str,
    device: str = "cpu",
) -> nn.Module:
    """Loads the EfficientNet-B0 audit model from a saved checkpoint.

    The model was fine-tuned on HAM10000 using the training script at
    scripts/train_baseline.py. It expects 224x224x3 input normalised with
    ImageNet mean and std.

    Args:
        model_path: Path to the .pth checkpoint file.
        device: Device to load the model onto ('cpu' or 'cuda').

    Returns:
        The loaded model in eval mode, moved to the specified device.

    Raises:
        FileNotFoundError: If model_path does not exist.
        RuntimeError: If the checkpoint cannot be loaded (e.g. architecture
            mismatch).
    """
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model checkpoint not found at {model_path}.\n"
            "Facilitators: upload the .pth file to Google Drive and update "
            "MODEL_PATH in the configuration cell."
        )

    model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=7)

    state_dict = torch.load(model_path, map_location=device)

    # Handle checkpoints saved with or without a 'model_state_dict' wrapper
    if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
        state_dict = state_dict["model_state_dict"]

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    print(
        f"Model loaded successfully from {model_path.name}\n"
        f"  Architecture : EfficientNet-B0\n"
        f"  Classes      : {len(CLASS_NAMES)} ({', '.join(CLASS_NAMES)})\n"
        f"  Device       : {device}"
    )

    return model


def run_inference(
    model: nn.Module,
    dataloader,
    device: str,
) -> Dict:
    """Runs a full inference pass over a DataLoader.

    Does not compute gradients. Displays a tqdm progress bar.

    Args:
        model: The model returned by load_audit_model (must be in eval mode).
        dataloader: A PyTorch DataLoader whose items are (image_tensor, label, image_id).
        device: Device string matching where the model lives.

    Returns:
        A dict with keys:
            predictions (List[int]): Predicted class index for each sample.
            probabilities (List[List[float]]): Per-class softmax probabilities.
            true_labels (List[int]): Ground-truth class indices.
            image_ids (List[str]): Image ID strings in dataset order.
    """
    all_predictions: List[int] = []
    all_probabilities: List[List[float]] = []
    all_true_labels: List[int] = []
    all_image_ids: List[str] = []

    model.eval()

    with torch.no_grad():
        for batch_images, batch_labels, batch_ids in tqdm(
            dataloader, desc="Running inference", unit="batch"
        ):
            batch_images = batch_images.to(device)
            logits = model(batch_images)
            probs = torch.softmax(logits, dim=1)

            preds = probs.argmax(dim=1).cpu().tolist()
            probs_list = probs.cpu().tolist()
            labels_list = (
                batch_labels.tolist()
                if hasattr(batch_labels, "tolist")
                else list(batch_labels)
            )

            all_predictions.extend(preds)
            all_probabilities.extend(probs_list)
            all_true_labels.extend(labels_list)
            all_image_ids.extend(list(batch_ids))

    return {
        "predictions": all_predictions,
        "probabilities": all_probabilities,
        "true_labels": all_true_labels,
        "image_ids": all_image_ids,
    }


def predict_single(
    model: nn.Module,
    pil_image: Image.Image,
    device: str,
) -> Dict:
    """Runs inference on a single PIL image.

    Applies the standard AUDIT_TRANSFORM before passing to the model.

    Args:
        model: The model returned by load_audit_model.
        pil_image: A PIL Image object (any size, RGB or convertible to RGB).
        device: Device string matching where the model lives.

    Returns:
        A dict with keys:
            predicted_class (str): The abbreviated class name (e.g. 'mel').
            confidence (float): Softmax probability of the predicted class.
            all_probabilities (dict): Maps class abbreviation -> probability
                for all 7 classes.
    """
    image = pil_image.convert("RGB")
    tensor = AUDIT_TRANSFORM(image).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()

    predicted_idx = int(np.argmax(probs))
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence = probs[predicted_idx]
    all_probs = {cls: probs[i] for i, cls in enumerate(CLASS_NAMES)}

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "all_probabilities": all_probs,
    }
