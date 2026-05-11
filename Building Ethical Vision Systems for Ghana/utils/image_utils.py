"""
image_utils.py — OpenCV helpers and preprocessing pipeline for Part 1.

All functions operate on numpy arrays. Colour space conventions:
  - Input/output default: RGB (not OpenCV's BGR)
  - Internally converts to BGR for OpenCV operations, converts back before returning
"""

from __future__ import annotations

import cv2
import numpy as np


def load_image(path: str, colour_space: str = "rgb") -> np.ndarray:
    """Load an image file and convert to the specified colour space.

    Args:
        path: Absolute or relative path to the image file.
        colour_space: One of 'rgb', 'bgr', 'hsv', 'gray'.

    Returns:
        Image as a numpy array in the requested colour space.

    Raises:
        FileNotFoundError: If the image cannot be loaded from path.
    """
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        raise FileNotFoundError(f"Could not load image: {path}")

    cs = colour_space.lower()
    if cs == "bgr":
        return img_bgr
    elif cs == "rgb":
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    elif cs == "hsv":
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    elif cs == "gray":
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Unknown colour_space '{colour_space}'. Use 'rgb', 'bgr', 'hsv', or 'gray'.")


def histogram_equalise(
    img: np.ndarray,
    method: str = "clahe",
    clip_limit: float = 2.0,
    tile_size: tuple = (8, 8),
) -> np.ndarray:
    """Apply histogram equalisation to enhance contrast.

    Operates on the luminance channel (converts to LAB internally) so colour
    information is preserved. Accepts RGB input, returns RGB output.

    Args:
        img: RGB image as uint8 numpy array, shape (H, W, 3) or (H, W).
        method: 'global' for standard equalisation, 'clahe' for adaptive (recommended).
        clip_limit: CLAHE clip limit — higher values give more contrast boost.
        tile_size: CLAHE tile grid size as (rows, cols).

    Returns:
        Equalised RGB image (or grayscale if input was grayscale).
    """
    if img.ndim == 2:
        # Grayscale path
        if method == "clahe":
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
            return clahe.apply(img)
        return cv2.equalizeHist(img)

    # Colour path: equalise only the L channel in LAB space
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    if method == "clahe":
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        l_eq = clahe.apply(l_ch)
    else:
        l_eq = cv2.equalizeHist(l_ch)

    lab_eq = cv2.merge([l_eq, a_ch, b_ch])
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)


def remove_shadow(
    img: np.ndarray,
    kernel_size: int = 7,
    blur_size: int = 21,
) -> np.ndarray:
    """Estimate and remove spatially varying illumination (shadow removal).

    Technique: dilate to fill the lesion region, then median-blur to estimate
    the background illumination field. Divide original by background and rescale.

    Args:
        img: RGB image as uint8 numpy array.
        kernel_size: Dilation kernel size (odd integer).
        blur_size: Median blur kernel size for background smoothing (odd integer).

    Returns:
        Shadow-corrected RGB image as uint8.
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    # Work channel by channel so colour information is preserved
    channels = cv2.split(img)
    result_channels = []
    for ch in channels:
        dilated = cv2.dilate(ch, kernel)
        bg = cv2.medianBlur(dilated, blur_size)
        # Avoid division by zero; scale to [0, 255]
        corrected = cv2.divide(ch.astype(np.float32), bg.astype(np.float32), scale=255)
        result_channels.append(np.clip(corrected, 0, 255).astype(np.uint8))
    return cv2.merge(result_channels)


def sharpen(
    img: np.ndarray,
    method: str = "unsharp",
    alpha: float = 0.5,
    sigma: float = 3.0,
) -> np.ndarray:
    """Sharpen an image using unsharp masking or a Laplacian kernel.

    Args:
        img: Grayscale or RGB image as uint8 numpy array.
        method: 'unsharp' for unsharp masking, 'kernel' for Laplacian sharpening.
        alpha: Unsharp mask strength. Higher values → more sharpening.
        sigma: Gaussian blur sigma used in unsharp masking.

    Returns:
        Sharpened image, same shape and dtype as input.
    """
    if method == "unsharp":
        blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)
        sharpened = cv2.addWeighted(img, 1.0 + alpha, blurred, -alpha, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    elif method == "kernel":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        return cv2.filter2D(img, -1, kernel)

    else:
        raise ValueError(f"Unknown method '{method}'. Use 'unsharp' or 'kernel'.")


def detect_edges(
    img: np.ndarray,
    method: str = "canny",
    low: int = 50,
    high: int = 150,
) -> np.ndarray:
    """Detect edges in a grayscale image.

    Args:
        img: Grayscale image as uint8 numpy array, shape (H, W).
             If RGB is passed it will be converted to grayscale automatically.
        method: 'canny', 'sobel_x', 'sobel_y', or 'sobel_magnitude'.
        low: Canny lower hysteresis threshold (ignored for Sobel methods).
        high: Canny upper hysteresis threshold (ignored for Sobel methods).

    Returns:
        Edge map as uint8 numpy array, shape (H, W).
    """
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    if method == "canny":
        return cv2.Canny(gray, low, high)

    elif method == "sobel_x":
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        return cv2.convertScaleAbs(sobel)

    elif method == "sobel_y":
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        return cv2.convertScaleAbs(sobel)

    elif method == "sobel_magnitude":
        sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sx ** 2 + sy ** 2)
        return cv2.convertScaleAbs(magnitude)

    else:
        raise ValueError(f"Unknown method '{method}'.")


def find_lesion_contour(edge_map: np.ndarray) -> tuple:
    """Find the largest contour in an edge map and compute lesion geometry.

    Args:
        edge_map: Binary or grayscale edge map, shape (H, W).

    Returns:
        Tuple of (largest_contour, bounding_rect, area, perimeter, circularity).
        - largest_contour: numpy array of shape (N, 1, 2), or None if none found.
        - bounding_rect: (x, y, w, h) tuple.
        - area: contour area in pixels².
        - perimeter: contour perimeter in pixels.
        - circularity: 4π·area / perimeter² — 1.0 is a perfect circle.
    """
    contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, (0, 0, edge_map.shape[1], edge_map.shape[0]), 0.0, 0.0, 0.0

    largest = max(contours, key=cv2.contourArea)
    bounding_rect = cv2.boundingRect(largest)
    area = cv2.contourArea(largest)
    perimeter = cv2.arcLength(largest, closed=True)
    circularity = (4 * np.pi * area / perimeter ** 2) if perimeter > 0 else 0.0

    return largest, bounding_rect, area, perimeter, circularity


def crop_to_lesion(
    img: np.ndarray,
    bounding_rect: tuple,
    padding: int = 10,
) -> np.ndarray:
    """Crop an image to the lesion bounding box with optional padding.

    Args:
        img: Input image, shape (H, W) or (H, W, C).
        bounding_rect: (x, y, w, h) as returned by find_lesion_contour.
        padding: Extra pixels added around the bounding box on each side.

    Returns:
        Cropped image region.
    """
    x, y, w, h = bounding_rect
    H, W = img.shape[:2]

    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(W, x + w + padding)
    y2 = min(H, y + h + padding)

    return img[y1:y2, x1:x2]


def preprocess_pipeline(
    img: np.ndarray,
    target_size: tuple = (224, 224),
) -> np.ndarray:
    """Run the full preprocessing pipeline on an RGB image.

    Pipeline: equalise (CLAHE) → shadow removal → sharpen → edge detect →
              find largest contour → crop to ROI → resize to target_size.

    Args:
        img: RGB image as uint8 numpy array.
        target_size: (width, height) to resize the final crop.

    Returns:
        Preprocessed RGB image of shape (target_size[1], target_size[0], 3).
    """
    equalised = histogram_equalise(img, method="clahe")
    no_shadow = remove_shadow(equalised)
    sharpened = sharpen(no_shadow, method="unsharp", alpha=0.5)

    gray = cv2.cvtColor(sharpened, cv2.COLOR_RGB2GRAY)
    edges = detect_edges(gray, method="canny", low=50, high=150)

    _, bounding_rect, _, _, _ = find_lesion_contour(edges)
    cropped = crop_to_lesion(img, bounding_rect, padding=10)

    return cv2.resize(cropped, target_size, interpolation=cv2.INTER_LANCZOS4)
