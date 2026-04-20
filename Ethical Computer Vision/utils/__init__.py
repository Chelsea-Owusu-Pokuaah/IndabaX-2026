"""
gdss-audit-lab utilities package.

Provides data loading, model inference, metrics computation, and
visualisation tools for The Audit lab notebook.
"""

from utils.data_loader import get_dataloader, get_dataset_info
from utils.model_loader import load_audit_model, run_inference, predict_single
from utils.metrics import (
    CLASS_NAMES,
    CLASS_LABELS,
    compute_metrics,
    build_failure_table,
    compute_fairness_metrics,
)
from utils.visualisation import (
    plot_confusion_matrix,
    plot_per_class_f1,
    plot_metric_comparison,
    plot_confidence_distribution,
    display_failure_grid,
    plot_options_comparison,
    plot_fitzpatrick_distribution,
)

__all__ = [
    "get_dataloader",
    "get_dataset_info",
    "load_audit_model",
    "run_inference",
    "predict_single",
    "CLASS_NAMES",
    "CLASS_LABELS",
    "compute_metrics",
    "build_failure_table",
    "compute_fairness_metrics",
    "plot_confusion_matrix",
    "plot_per_class_f1",
    "plot_metric_comparison",
    "plot_confidence_distribution",
    "display_failure_grid",
    "plot_options_comparison",
    "plot_fitzpatrick_distribution",
]
