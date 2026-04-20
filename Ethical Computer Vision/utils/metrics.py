"""
metrics.py — Evaluation metrics and fairness measures for The Audit lab.

Computes standard classification metrics, builds structured failure tables,
and quantifies performance gaps between demographic groups.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
)


# ---------------------------------------------------------------------------
# Class definitions
# ---------------------------------------------------------------------------

CLASS_NAMES: List[str] = ["nv", "mel", "bcc", "akiec", "bkl", "df", "vasc"]

CLASS_LABELS: Dict[str, str] = {
    "nv": "Melanocytic Nevi",
    "mel": "Melanoma",
    "bcc": "Basal Cell Carcinoma",
    "akiec": "Actinic Keratoses",
    "bkl": "Benign Keratoses",
    "df": "Dermatofibroma",
    "vasc": "Vascular Lesions",
}

# Error type labels used in the failure table
ERROR_FALSE_NEGATIVE = "false_negative"
ERROR_FALSE_POSITIVE = "false_positive"
ERROR_HIGH_CONF_WRONG = "high_conf_wrong"
ERROR_CORRECT = "correct"

# Confidence threshold above which a wrong prediction is flagged as
# 'high_conf_wrong'. Set to match CONFIDENCE_THRESHOLD in the notebook.
HIGH_CONFIDENCE_THRESHOLD = 0.80


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------


def compute_metrics(
    predictions: List[int],
    true_labels: List[int],
    probabilities: List[List[float]],
) -> Dict:
    """Computes classification metrics for a set of predictions.

    Args:
        predictions: Predicted class indices, one per sample.
        true_labels: Ground-truth class indices, one per sample.
        probabilities: Per-class softmax probabilities, shape (n_samples, 7).

    Returns:
        A dict containing:
            overall_accuracy (float): Fraction of correct predictions.
            per_class_accuracy (dict): Class abbreviation -> accuracy.
            macro_f1 (float): Unweighted mean F1 across all classes.
            weighted_f1 (float): F1 weighted by class support.
            per_class_f1 (dict): Class abbreviation -> F1 score.
            confusion_matrix (np.ndarray): Shape (7, 7).
            avg_confidence_correct (float): Mean max-prob for correct preds.
            avg_confidence_wrong (float): Mean max-prob for wrong preds.
    """
    preds = np.array(predictions)
    labels = np.array(true_labels)
    probs = np.array(probabilities)

    overall_accuracy = float(accuracy_score(labels, preds))

    # Per-class accuracy
    per_class_accuracy: Dict[str, float] = {}
    for i, cls in enumerate(CLASS_NAMES):
        mask = labels == i
        if mask.sum() == 0:
            per_class_accuracy[cls] = float("nan")
        else:
            per_class_accuracy[cls] = float(accuracy_score(labels[mask], preds[mask]))

    macro_f1 = float(
        f1_score(labels, preds, average="macro", zero_division=0)
    )
    weighted_f1 = float(
        f1_score(labels, preds, average="weighted", zero_division=0)
    )

    per_class_f1_values = f1_score(
        labels, preds, average=None, zero_division=0, labels=list(range(7))
    )
    per_class_f1 = {
        cls: float(per_class_f1_values[i]) for i, cls in enumerate(CLASS_NAMES)
    }

    cm = confusion_matrix(labels, preds, labels=list(range(7)))

    # Confidence stats
    max_probs = probs.max(axis=1)
    correct_mask = preds == labels
    avg_confidence_correct = (
        float(max_probs[correct_mask].mean()) if correct_mask.any() else float("nan")
    )
    avg_confidence_wrong = (
        float(max_probs[~correct_mask].mean())
        if (~correct_mask).any()
        else float("nan")
    )

    return {
        "overall_accuracy": overall_accuracy,
        "per_class_accuracy": per_class_accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class_f1": per_class_f1,
        "confusion_matrix": cm,
        "avg_confidence_correct": avg_confidence_correct,
        "avg_confidence_wrong": avg_confidence_wrong,
    }


# ---------------------------------------------------------------------------
# Failure table
# ---------------------------------------------------------------------------


def build_failure_table(
    predictions: List[int],
    true_labels: List[int],
    probabilities: List[List[float]],
    image_ids: List[str],
    confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD,
) -> pd.DataFrame:
    """Builds a structured DataFrame of per-image prediction results.

    Each row represents one image. Correct predictions are included (with
    error_type='correct') so the table can be filtered in any direction.

    Error type logic:
        - correct: prediction matches true label
        - high_conf_wrong: wrong AND confidence >= confidence_threshold
        - false_negative: wrong AND predicted a benign class when true was malignant
          (mel, bcc, akiec)
        - false_positive: wrong AND predicted a malignant class when true was benign

    Args:
        predictions: Predicted class indices.
        true_labels: Ground-truth class indices.
        probabilities: Per-class softmax probabilities, shape (n_samples, 7).
        image_ids: Image ID strings in dataset order.
        confidence_threshold: Confidence above which a wrong prediction is
            flagged as high_conf_wrong. Default matches CONFIDENCE_THRESHOLD.

    Returns:
        A pandas DataFrame with columns:
            image_id, true_label, true_label_name, predicted_label,
            predicted_label_name, confidence, error_type.
        Sorted by confidence descending.
    """
    MALIGNANT_CLASSES = {"mel", "bcc", "akiec"}

    rows = []
    for img_id, pred, true, probs in zip(image_ids, predictions, true_labels, probabilities):
        probs_arr = np.array(probs)
        confidence = float(probs_arr.max())
        pred_cls = CLASS_NAMES[pred]
        true_cls = CLASS_NAMES[true]

        if pred == true:
            error_type = ERROR_CORRECT
        elif confidence >= confidence_threshold:
            error_type = ERROR_HIGH_CONF_WRONG
        elif (
            true_cls in MALIGNANT_CLASSES
            and pred_cls not in MALIGNANT_CLASSES
        ):
            error_type = ERROR_FALSE_NEGATIVE
        elif (
            true_cls not in MALIGNANT_CLASSES
            and pred_cls in MALIGNANT_CLASSES
        ):
            error_type = ERROR_FALSE_POSITIVE
        else:
            # Wrong, but doesn't fit the cleaner categories above —
            # still report as wrong for completeness
            error_type = "wrong_other"

        rows.append(
            {
                "image_id": img_id,
                "true_label": true,
                "true_label_name": CLASS_LABELS[true_cls],
                "predicted_label": pred,
                "predicted_label_name": CLASS_LABELS[pred_cls],
                "confidence": round(confidence, 4),
                "error_type": error_type,
            }
        )

    df = pd.DataFrame(rows).sort_values("confidence", ascending=False).reset_index(
        drop=True
    )
    return df


# ---------------------------------------------------------------------------
# Fairness metrics
# ---------------------------------------------------------------------------


def compute_fairness_metrics(
    metrics_group_a: Dict,
    metrics_group_b: Dict,
) -> Dict:
    """Computes performance gaps between two groups.

    Intended to compare HAM10000 (Group A, predominantly skin types I-III)
    against the African-context dataset (Group B, skin types V-VI).

    Args:
        metrics_group_a: Output of compute_metrics() for group A.
        metrics_group_b: Output of compute_metrics() for group B.

    Returns:
        A dict with keys:
            accuracy_gap (float): Group A accuracy minus Group B accuracy.
                Positive means A performs better than B.
            macro_f1_gap (float): Macro F1 gap (A minus B).
            weighted_f1_gap (float): Weighted F1 gap (A minus B).
            per_class_accuracy_gap (dict): Class abbreviation ->
                accuracy gap (A minus B). NaN where data is unavailable.
            per_class_f1_gap (dict): Class abbreviation -> F1 gap (A minus B).
    """
    accuracy_gap = (
        metrics_group_a["overall_accuracy"] - metrics_group_b["overall_accuracy"]
    )
    macro_f1_gap = metrics_group_a["macro_f1"] - metrics_group_b["macro_f1"]
    weighted_f1_gap = metrics_group_a["weighted_f1"] - metrics_group_b["weighted_f1"]

    per_class_accuracy_gap = {
        cls: (
            metrics_group_a["per_class_accuracy"].get(cls, float("nan"))
            - metrics_group_b["per_class_accuracy"].get(cls, float("nan"))
        )
        for cls in CLASS_NAMES
    }

    per_class_f1_gap = {
        cls: (
            metrics_group_a["per_class_f1"].get(cls, float("nan"))
            - metrics_group_b["per_class_f1"].get(cls, float("nan"))
        )
        for cls in CLASS_NAMES
    }

    return {
        "accuracy_gap": accuracy_gap,
        "macro_f1_gap": macro_f1_gap,
        "weighted_f1_gap": weighted_f1_gap,
        "per_class_accuracy_gap": per_class_accuracy_gap,
        "per_class_f1_gap": per_class_f1_gap,
    }
