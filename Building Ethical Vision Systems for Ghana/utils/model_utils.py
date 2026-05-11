"""
model_utils.py — Model loading, inference, and feature extraction for Part 1.

Supports EfficientNet-B0, YOLOv8, ViT, and CLIP. All functions are
device-aware and handle CPU/GPU placement transparently.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image


# ---------------------------------------------------------------------------
# ImageNet normalisation (used by all timm / torchvision models)
# ---------------------------------------------------------------------------

_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD = [0.229, 0.224, 0.225]

_PREPROCESS = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
])


def load_efficientnet(
    num_classes: int = 7,
    pretrained_path: Optional[str] = None,
    device: str = "cpu",
) -> nn.Module:
    """Load EfficientNet-B0.

    Args:
        num_classes: Number of output classes. Use 1000 for ImageNet weights.
        pretrained_path: Path to a fine-tuned checkpoint (.pth). If None,
            loads timm ImageNet-pretrained weights.
        device: 'cpu' or 'cuda'.

    Returns:
        EfficientNet-B0 model in eval mode on the requested device.
    """
    import timm

    if pretrained_path is None:
        model = timm.create_model(
            "efficientnet_b0", pretrained=True, num_classes=num_classes
        )
    else:
        model = timm.create_model(
            "efficientnet_b0", pretrained=False, num_classes=num_classes
        )
        state = torch.load(pretrained_path, map_location=device)
        model.load_state_dict(state)

    model = model.to(device)
    model.eval()
    return model


def load_yolo(model_size: str = "n", device: str = "cpu"):
    """Load a YOLOv8 model from Ultralytics.

    Args:
        model_size: One of 'n' (nano), 's', 'm', 'l', 'x'.
        device: 'cpu' or 'cuda'.

    Returns:
        Ultralytics YOLO model instance.
    """
    from ultralytics import YOLO

    model_name = f"yolov8{model_size}.pt"
    model = YOLO(model_name)
    return model


def load_vit(
    model_name: str = "vit_base_patch16_224",
    device: str = "cpu",
) -> nn.Module:
    """Load a Vision Transformer from timm.

    Args:
        model_name: timm model identifier, e.g. 'vit_base_patch16_224',
            'vit_small_patch16_224', 'swin_tiny_patch4_window7_224'.
        device: 'cpu' or 'cuda'.

    Returns:
        ViT model in eval mode on the requested device.
    """
    import timm

    model = timm.create_model(model_name, pretrained=True)
    model = model.to(device)
    model.eval()
    return model


def load_clip(
    model_name: str = "openai/clip-vit-base-patch32",
    device: str = "cpu",
) -> tuple:
    """Load a CLIP model from HuggingFace transformers.

    Args:
        model_name: HuggingFace model identifier.
        device: 'cpu' or 'cuda'.

    Returns:
        Tuple of (CLIPModel, CLIPProcessor) both on the requested device.
    """
    from transformers import CLIPModel, CLIPProcessor

    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name).to(device)
    model.eval()
    return model, processor


def get_image_tensor(
    pil_image: Image.Image,
    device: str = "cpu",
) -> torch.Tensor:
    """Apply ImageNet normalisation and return a batched tensor.

    Args:
        pil_image: PIL RGB image.
        device: Target device.

    Returns:
        Float tensor of shape (1, 3, 224, 224).
    """
    tensor = _PREPROCESS(pil_image).unsqueeze(0)
    return tensor.to(device)


def predict_class(
    model: nn.Module,
    image_tensor: torch.Tensor,
    class_names: list,
) -> dict:
    """Run a forward pass and return the top prediction.

    Args:
        model: Pretrained classification model in eval mode.
        image_tensor: Batched image tensor, shape (1, 3, H, W).
        class_names: List of class name strings matching model output indices.

    Returns:
        Dict with keys 'predicted' (str), 'confidence' (float),
        'all' (dict mapping class_name → probability).
    """
    device = next(model.parameters()).device
    tensor = image_tensor.to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    top_idx = int(np.argmax(probs))
    return {
        "predicted": class_names[top_idx],
        "confidence": float(probs[top_idx]),
        "all": {name: float(p) for name, p in zip(class_names, probs)},
    }


def extract_feature_maps(
    model: nn.Module,
    image_tensor: torch.Tensor,
    layer_names: list,
) -> dict:
    """Extract intermediate feature maps using forward hooks.

    Args:
        model: A timm / torchvision model.
        image_tensor: Batched image tensor, shape (1, 3, H, W).
        layer_names: List of attribute paths to hook, e.g.
            ['blocks.0', 'blocks.3', 'blocks.6'].

    Returns:
        Dict mapping layer_name → numpy array of shape (C, H, W).
    """
    device = next(model.parameters()).device
    tensor = image_tensor.to(device)
    feature_maps: dict = {}
    hooks = []

    def _make_hook(name: str):
        def hook(module, input, output):
            activation = output.detach().cpu()
            if activation.ndim == 4:
                feature_maps[name] = activation[0].numpy()  # (C, H, W)
            elif activation.ndim == 3:
                # Transformer sequence output (1, N, D) — reshape to square
                feature_maps[name] = activation[0].numpy()
        return hook

    for name in layer_names:
        try:
            module = model
            for attr in name.split("."):
                module = getattr(module, attr)
            h = module.register_forward_hook(_make_hook(name))
            hooks.append(h)
        except AttributeError:
            print(f"[extract_feature_maps] Layer '{name}' not found — skipping.")

    with torch.no_grad():
        try:
            model(tensor)
        except Exception as exc:
            print(f"[extract_feature_maps] Forward pass error: {exc}")

    for h in hooks:
        h.remove()

    return feature_maps


def compute_gradcam(
    model: nn.Module,
    image_tensor: torch.Tensor,
    target_class: int,
    target_layer_name: str,
) -> np.ndarray:
    """Compute a Grad-CAM heatmap for the specified class and layer.

    Args:
        model: Classification model. Must support gradient computation.
        image_tensor: Batched image tensor, shape (1, 3, H, W).
        target_class: Class index to explain.
        target_layer_name: Dot-separated attribute path to the target conv layer.

    Returns:
        Heatmap as float32 numpy array, shape (H, W), values in [0, 1].
        Returns zeros array on failure.
    """
    device = next(model.parameters()).device
    tensor = image_tensor.to(device).requires_grad_(False)

    activations: list = []
    gradients: list = []

    try:
        module = model
        for attr in target_layer_name.split("."):
            module = getattr(module, attr)
    except AttributeError:
        print(f"[compute_gradcam] Layer '{target_layer_name}' not found.")
        return np.zeros((7, 7), dtype=np.float32)

    def _fwd_hook(mod, inp, out):
        activations.append(out)

    def _bwd_hook(mod, grad_in, grad_out):
        gradients.append(grad_out[0])

    fh = module.register_forward_hook(_fwd_hook)
    bh = module.register_full_backward_hook(_bwd_hook)

    model.eval()
    output = model(tensor.requires_grad_(True))
    model.zero_grad()
    output[0, target_class].backward()

    fh.remove()
    bh.remove()

    if not activations or not gradients:
        return np.zeros((7, 7), dtype=np.float32)

    act = activations[0].detach().cpu().numpy()[0]   # (C, H, W)
    grad = gradients[0].detach().cpu().numpy()[0]    # (C, H, W)

    weights = grad.mean(axis=(1, 2))                 # (C,)
    cam = np.sum(weights[:, None, None] * act, axis=0)
    cam = np.maximum(cam, 0)                         # ReLU
    cam -= cam.min()
    if cam.max() > 0:
        cam /= cam.max()

    return cam.astype(np.float32)


def clip_zero_shot(
    model,
    processor,
    image: Image.Image,
    prompts: list,
    device: str = "cpu",
) -> dict:
    """Run CLIP zero-shot classification.

    Args:
        model: CLIPModel instance.
        processor: CLIPProcessor instance.
        image: PIL RGB image.
        prompts: List of text prompt strings.
        device: Target device.

    Returns:
        Dict mapping prompt string → probability (softmax over prompts).
    """
    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image  # (1, n_prompts)
        probs = logits.softmax(dim=1)[0].cpu().numpy()

    return {prompt: float(p) for prompt, p in zip(prompts, probs)}
