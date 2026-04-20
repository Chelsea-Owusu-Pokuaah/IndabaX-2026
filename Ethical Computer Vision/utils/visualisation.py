"""
visualisation.py — All plotting functions for The Audit lab.

Consistent colour palette across all charts:
  Primary  : Teal   #028090
  Secondary: Navy   #1A2535
  Warning  : Amber  #D97706

All functions return the matplotlib Figure object for inline display
and optionally save to assets/ when save=True.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# Palette and base style
# ---------------------------------------------------------------------------

TEAL = "#028090"
NAVY = "#1A2535"
AMBER = "#D97706"
RED = "#DC2626"
LIGHT_GREY = "#F3F4F6"
MID_GREY = "#9CA3AF"

CLASS_NAMES = ["nv", "mel", "bcc", "akiec", "bkl", "df", "vasc"]
CLASS_LABELS = {
    "nv": "Melanocytic\nNevi",
    "mel": "Melanoma",
    "bcc": "Basal Cell\nCarcinoma",
    "akiec": "Actinic\nKeratoses",
    "bkl": "Benign\nKeratoses",
    "df": "Dermatofibroma",
    "vasc": "Vascular\nLesions",
}

ASSETS_DIR = Path("assets")


def _save_figure(fig: Figure, filename: str) -> None:
    """Saves figure to the assets directory."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS_DIR / filename, dpi=150, bbox_inches="tight")
    print(f"Saved: assets/{filename}")


def _apply_base_style() -> None:
    """Applies the base seaborn style for all plots."""
    plt.style.use("seaborn-v0_8-whitegrid")


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------


def plot_confusion_matrix(
    true_labels: List[int],
    predictions: List[int],
    class_names: Optional[List[str]] = None,
    title: str = "",
    figsize: tuple = (9, 7),
    save: bool = False,
) -> Figure:
    """Plots a normalised confusion matrix as a seaborn heatmap.

    Args:
        true_labels: Ground-truth class indices.
        predictions: Predicted class indices.
        class_names: Display names for each class. Defaults to CLASS_LABELS values.
        title: Plot title. Defaults to 'Confusion Matrix'.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/confusion_matrix.png.

    Returns:
        The matplotlib Figure object.
    """
    from sklearn.metrics import confusion_matrix as sk_cm

    _apply_base_style()
    labels = class_names or [CLASS_LABELS[c] for c in CLASS_NAMES]

    cm = sk_cm(true_labels, predictions, labels=list(range(len(labels))))
    cm_normalised = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    cm_normalised = np.nan_to_num(cm_normalised)

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm_normalised,
        annot=True,
        fmt=".2f",
        cmap=sns.light_palette(TEAL, as_cmap=True),
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
        linewidths=0.5,
        linecolor=LIGHT_GREY,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title(title or "Confusion Matrix", fontsize=14, fontweight="bold", color=NAVY, pad=12)
    ax.set_ylabel("True Label", fontsize=11, color=NAVY)
    ax.set_xlabel("Predicted Label", fontsize=11, color=NAVY)
    ax.tick_params(axis="both", labelsize=8)
    plt.tight_layout()

    if save:
        _save_figure(fig, "confusion_matrix.png")

    return fig


# ---------------------------------------------------------------------------
# Per-class F1 bar chart
# ---------------------------------------------------------------------------


def plot_per_class_f1(
    metrics: Dict,
    title: str = "",
    figsize: tuple = (9, 4),
    save: bool = False,
) -> Figure:
    """Plots per-class F1 scores as a horizontal bar chart, sorted descending.

    Args:
        metrics: Output of utils.metrics.compute_metrics().
        title: Plot title.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/per_class_f1.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()

    per_class_f1 = metrics["per_class_f1"]
    sorted_items = sorted(per_class_f1.items(), key=lambda x: x[1], reverse=True)
    classes, scores = zip(*sorted_items)
    display_names = [CLASS_LABELS.get(c, c).replace("\n", " ") for c in classes]

    colours = [AMBER if s < 0.5 else TEAL for s in scores]

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(display_names, scores, color=colours, edgecolor="white", linewidth=0.5)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_width() + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center",
            ha="left",
            fontsize=9,
            color=NAVY,
        )

    ax.set_xlim(0, 1.12)
    ax.set_xlabel("F1 Score", fontsize=11, color=NAVY)
    ax.set_title(title or "Per-Class F1 Score", fontsize=13, fontweight="bold", color=NAVY, pad=10)
    ax.tick_params(axis="y", labelsize=9)
    ax.axvline(x=0.5, color=AMBER, linestyle="--", linewidth=1, alpha=0.6, label="F1 = 0.50")
    ax.legend(fontsize=8)
    ax.invert_yaxis()
    plt.tight_layout()

    if save:
        _save_figure(fig, "per_class_f1.png")

    return fig


# ---------------------------------------------------------------------------
# Side-by-side metric comparison — the central visual of the lab
# ---------------------------------------------------------------------------


def plot_metric_comparison(
    metrics_a: Dict,
    metrics_b: Dict,
    label_a: str = "HAM10000 Test",
    label_b: str = "African Context",
    figsize: tuple = (14, 6),
    save: bool = False,
) -> Figure:
    """Side-by-side bar chart comparing two datasets across all key metrics.

    This is the central visual of the lab. The performance gap must be
    immediately legible. Overall accuracy, macro F1, and per-class F1 are
    shown together in a single figure.

    Args:
        metrics_a: compute_metrics() output for the first dataset (HAM10000).
        metrics_b: compute_metrics() output for the second dataset (African-context).
        label_a: Legend label for the first dataset.
        label_b: Legend label for the second dataset.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/metric_comparison.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()

    # Build the value arrays
    metric_keys = ["overall_accuracy", "macro_f1"] + [
        f"f1_{cls}" for cls in CLASS_NAMES
    ]
    display_names = ["Overall\nAccuracy", "Macro\nF1"] + [
        CLASS_LABELS[c] for c in CLASS_NAMES
    ]

    values_a = [metrics_a["overall_accuracy"], metrics_a["macro_f1"]] + [
        metrics_a["per_class_f1"].get(cls, 0.0) for cls in CLASS_NAMES
    ]
    values_b = [metrics_b["overall_accuracy"], metrics_b["macro_f1"]] + [
        metrics_b["per_class_f1"].get(cls, 0.0) for cls in CLASS_NAMES
    ]

    n = len(display_names)
    x = np.arange(n)
    width = 0.38

    fig, ax = plt.subplots(figsize=figsize)

    bars_a = ax.bar(x - width / 2, values_a, width, color=TEAL, label=label_a, zorder=3)
    bars_b = ax.bar(x + width / 2, values_b, width, color=AMBER, label=label_b, zorder=3)

    # Annotate values on bars
    for bar in bars_a:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{bar.get_height():.2f}",
            ha="center",
            va="bottom",
            fontsize=7,
            color=NAVY,
        )
    for bar in bars_b:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{bar.get_height():.2f}",
            ha="center",
            va="bottom",
            fontsize=7,
            color=NAVY,
        )

    # Draw a vertical separator between summary metrics and per-class metrics
    ax.axvline(x=1.5, color=MID_GREY, linestyle="--", linewidth=1, alpha=0.5)
    ax.text(1.55, 0.95, "per-class F1 →", fontsize=8, color=MID_GREY, va="top")

    ax.set_xticks(x)
    ax.set_xticklabels(display_names, fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score", fontsize=11, color=NAVY)
    ax.set_title(
        f"Model Performance: {label_a} vs {label_b}",
        fontsize=14,
        fontweight="bold",
        color=NAVY,
        pad=12,
    )
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(axis="y", alpha=0.4, zorder=0)
    plt.tight_layout()

    if save:
        _save_figure(fig, "metric_comparison.png")

    return fig


# ---------------------------------------------------------------------------
# Confidence distribution
# ---------------------------------------------------------------------------


def plot_confidence_distribution(
    probs_a: List[List[float]],
    probs_b: List[List[float]],
    label_a: str = "HAM10000",
    label_b: str = "African Context",
    figsize: tuple = (8, 4),
    save: bool = False,
) -> Figure:
    """Overlaid histograms of max confidence scores for two datasets.

    This plot surfaces that the model is equally confident on both datasets
    despite being far less accurate on the African-context set.

    Args:
        probs_a: Per-class probabilities for dataset A, shape (n_samples, 7).
        probs_b: Per-class probabilities for dataset B, shape (n_samples, 7).
        label_a: Legend label for dataset A.
        label_b: Legend label for dataset B.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/confidence_distribution.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()

    max_conf_a = [max(p) for p in probs_a]
    max_conf_b = [max(p) for p in probs_b]

    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(max_conf_a, bins=30, color=TEAL, alpha=0.65, label=label_a, density=True)
    ax.hist(max_conf_b, bins=30, color=AMBER, alpha=0.65, label=label_b, density=True)

    ax.axvline(x=0.8, color=RED, linestyle="--", linewidth=1.2, label="Threshold (0.80)")

    ax.set_xlabel("Max Confidence Score", fontsize=11, color=NAVY)
    ax.set_ylabel("Density", fontsize=11, color=NAVY)
    ax.set_title(
        "Model Confidence Distribution — Both Datasets",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        pad=10,
    )
    ax.legend(fontsize=9)
    # Annotation callout
    ax.text(
        0.72,
        ax.get_ylim()[1] * 0.85,
        "⚠ High confidence\ndoes not mean\ncorrect",
        fontsize=8,
        color=AMBER,
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=AMBER, alpha=0.8),
    )
    plt.tight_layout()

    if save:
        _save_figure(fig, "confidence_distribution.png")

    return fig


# ---------------------------------------------------------------------------
# Failure image grid
# ---------------------------------------------------------------------------


def display_failure_grid(
    images: List,
    predictions: List[str],
    true_labels: List[str],
    confidences: List[float],
    fitzpatrick_types: Optional[List] = None,
    n: int = 8,
    title: str = "",
    figsize: tuple = (14, 7),
    save: bool = False,
) -> Figure:
    """Grid of images showing model failures with labels and confidence scores.

    Each image shows:
        - Top caption: true label (green)
        - Bottom caption: predicted label + confidence (red if wrong)
        - Optional Fitzpatrick type if available

    Args:
        images: List of PIL Images or numpy arrays.
        predictions: Predicted class name strings.
        true_labels: True class name strings.
        confidences: Confidence scores for each prediction.
        fitzpatrick_types: Optional list of Fitzpatrick type integers or None.
        n: Number of images to display (will show min(n, len(images))).
        title: Figure title.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/failure_grid.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()
    n = min(n, len(images))
    cols = 4
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    axes = np.array(axes).flatten()

    for i in range(n):
        ax = axes[i]
        img = images[i]

        # Handle both PIL Images and numpy arrays
        if hasattr(img, "numpy"):
            img = img.numpy()
        if isinstance(img, np.ndarray) and img.shape[0] == 3:
            img = np.transpose(img, (1, 2, 0))
            # Reverse ImageNet normalisation for display
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img = (img * std + mean).clip(0, 1)

        ax.imshow(img)
        ax.axis("off")

        is_wrong = predictions[i] != true_labels[i]
        label_colour = RED if is_wrong else TEAL

        fitz_str = ""
        if fitzpatrick_types and fitzpatrick_types[i] is not None:
            fitz_str = f"\nFitzpatrick Type {fitzpatrick_types[i]}"

        ax.set_title(
            f"True: {true_labels[i]}",
            fontsize=7,
            color=TEAL,
            pad=2,
        )
        ax.text(
            0.5,
            -0.05,
            f"Pred: {predictions[i]} ({confidences[i]:.0%}){fitz_str}",
            transform=ax.transAxes,
            fontsize=7,
            color=label_colour,
            ha="center",
            va="top",
        )

    # Hide unused axes
    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.suptitle(
        title or "Model Failures — Worst Cases",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        y=1.01,
    )
    plt.tight_layout()

    if save:
        _save_figure(fig, "failure_grid.png")

    return fig


# ---------------------------------------------------------------------------
# Options A/B/C comparison heatmap
# ---------------------------------------------------------------------------


def plot_options_comparison(
    figsize: tuple = (8, 4),
    save: bool = False,
) -> Figure:
    """Qualitative heatmap comparing deployment options A, B, and C.

    Compares three options across four dimensions using qualitative
    ratings (Low / Med / High) rendered as a colour-coded table.

    Args:
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/options_comparison.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()

    options = ["Option A\nCollect & Fine-tune", "Option B\nRestricted + Human Review", "Option C\nHalt Deployment"]
    dimensions = ["Time to\nDeployment", "Data Collection\nBurden", "Risk to\nPatient", "Risk to\nStartup"]

    # Qualitative values — 0 = Low, 1 = Med, 2 = High
    values = np.array(
        [
            [2, 2, 1, 1],  # Option A: slow, high effort, medium patient risk, low startup risk
            [1, 0, 1, 1],  # Option B: medium speed, low effort, medium patient risk, medium startup risk
            [0, 0, 0, 2],  # Option C: no deployment now, no data effort, low patient risk, high startup risk
        ]
    )
    labels = np.array(
        [
            ["High", "High", "Med", "Low"],
            ["Med", "Low", "Med", "Med"],
            ["—", "—", "Low", "High"],
        ]
    )

    # Custom colour map: green (0=Low) → amber (1=Med) → red (2=High)
    cmap = plt.cm.RdYlGn_r
    norm = plt.Normalize(vmin=0, vmax=2)

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(values, cmap=cmap, norm=norm, aspect="auto")

    ax.set_xticks(np.arange(len(dimensions)))
    ax.set_xticklabels(dimensions, fontsize=9, color=NAVY)
    ax.set_yticks(np.arange(len(options)))
    ax.set_yticklabels(options, fontsize=9, color=NAVY)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Annotate cells
    for i in range(len(options)):
        for j in range(len(dimensions)):
            ax.text(
                j,
                i,
                labels[i, j],
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color="white" if values[i, j] == 2 else NAVY,
            )

    ax.set_title(
        "Deployment Options — Risk and Burden Comparison",
        fontsize=12,
        fontweight="bold",
        color=NAVY,
        pad=30,
    )

    # Add legend
    legend_handles = [
        mpatches.Patch(color=cmap(norm(0)), label="Low"),
        mpatches.Patch(color=cmap(norm(1)), label="Med"),
        mpatches.Patch(color=cmap(norm(2)), label="High"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower right",
        bbox_to_anchor=(1.0, -0.18),
        ncol=3,
        fontsize=8,
        frameon=True,
    )

    plt.tight_layout()

    if save:
        _save_figure(fig, "options_comparison.png")

    return fig


# ---------------------------------------------------------------------------
# Fitzpatrick distribution
# ---------------------------------------------------------------------------


def plot_fitzpatrick_distribution(
    distribution: Dict,
    dataset_name: str = "Dataset",
    figsize: tuple = (7, 4),
    save: bool = False,
) -> Figure:
    """Bar chart of Fitzpatrick skin type representation.

    Args:
        distribution: Dict mapping Fitzpatrick type (int 1–6) to count or
            percentage. Use estimated values for HAM10000.
        dataset_name: Name shown in the title.
        figsize: Figure dimensions in inches.
        save: If True, saves to assets/fitzpatrick_distribution.png.

    Returns:
        The matplotlib Figure object.
    """
    _apply_base_style()

    types = sorted(distribution.keys())
    counts = [distribution[t] for t in types]
    total = sum(counts)
    percentages = [c / total * 100 if total > 0 else 0 for c in counts]

    type_labels = [f"Type {t}" for t in types]
    # Types V and VI are highlighted in amber to draw attention to underrepresentation
    colours = [AMBER if t >= 5 else TEAL for t in types]

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(type_labels, percentages, color=colours, edgecolor="white", linewidth=0.8)

    for bar, pct in zip(bars, percentages):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{pct:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color=NAVY,
        )

    ax.set_ylabel("Percentage of Dataset (%)", fontsize=10, color=NAVY)
    ax.set_title(
        f"Fitzpatrick Skin Type Distribution — {dataset_name}",
        fontsize=12,
        fontweight="bold",
        color=NAVY,
        pad=10,
    )

    legend_handles = [
        mpatches.Patch(color=TEAL, label="Types I–IV (represented)"),
        mpatches.Patch(color=AMBER, label="Types V–VI (underrepresented)"),
    ]
    ax.legend(handles=legend_handles, fontsize=8, loc="upper right")
    ax.set_ylim(0, max(percentages) * 1.25)
    plt.tight_layout()

    if save:
        _save_figure(fig, f"fitzpatrick_{dataset_name.lower().replace(' ', '_')}.png")

    return fig
