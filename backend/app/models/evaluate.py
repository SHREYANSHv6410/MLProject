from typing import Dict, Any, Tuple, List
import numpy as np


def _trapezoid_auc(y: List[float], x: List[float]) -> float:
    """Manual trapezoidal numerical integration compatible with all NumPy versions."""
    total = 0.0
    for i in range(len(x) - 1):
        dx = x[i + 1] - x[i]
        avg_y = (y[i] + y[i + 1]) / 2.0
        total += avg_y * dx
    return float(np.clip(total, 0.0, 1.0))


def compute_roc_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Compute Area Under the Receiver Operating Characteristic Curve."""
    if len(np.unique(y_true)) < 2:
        return 0.5
    desc_order = np.argsort(y_prob)[::-1]
    y_true_sorted = y_true[desc_order]
    
    n_pos = np.sum(y_true_sorted == 1)
    n_neg = len(y_true_sorted) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
        
    tp = 0
    fp = 0
    tpr_list = [0.0]
    fpr_list = [0.0]
    
    for label in y_true_sorted:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / n_pos)
        fpr_list.append(fp / n_neg)
        
    return _trapezoid_auc(tpr_list, fpr_list)


def compute_pr_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Compute Area Under the Precision-Recall Curve (Average Precision)."""
    if len(np.unique(y_true)) < 2:
        return 0.5
    desc_order = np.argsort(y_prob)[::-1]
    y_true_sorted = y_true[desc_order]
    
    n_pos = np.sum(y_true_sorted == 1)
    if n_pos == 0:
        return 0.0
        
    tp = 0
    fp = 0
    precisions = [1.0]
    recalls = [0.0]
    
    for label in y_true_sorted:
        if label == 1:
            tp += 1
        else:
            fp += 1
        precisions.append(tp / (tp + fp))
        recalls.append(tp / n_pos)
        
    return _trapezoid_auc(precisions, recalls)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray
) -> Dict[str, Any]:
    """
    Compute rigorous classification and probability calibration metrics.
    All evaluations are on held-out test data.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)

    # Confusion matrix
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    n = len(y_true) or 1
    accuracy = (tp + tn) / n
    pos_actual = max(1, tp + fn)
    neg_actual = max(1, tn + fp)
    pos_pred = max(1, tp + fp)

    recall = tp / pos_actual
    spec = tn / neg_actual
    balanced_acc = (recall + spec) / 2.0
    precision = tp / pos_pred
    f1 = (2 * precision * recall) / max(1e-8, (precision + recall))
    brier = float(np.mean((y_prob - y_true) ** 2))

    roc_auc = compute_roc_auc(y_true, y_prob)
    pr_auc = compute_pr_auc(y_true, y_prob)

    # Calibration Curve (5 uniform probability bins)
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    calib_points = []
    for b_idx in range(len(bins) - 1):
        low, high = bins[b_idx], bins[b_idx + 1]
        mask = (y_prob >= low) & (y_prob <= high if b_idx == len(bins) - 2 else y_prob < high)
        if np.any(mask):
            calib_points.append({
                "bin": b_idx + 1,
                "predicted_probability": float(round(float(np.mean(y_prob[mask])), 4)),
                "true_frequency": float(round(float(np.mean(y_true[mask])), 4))
            })

    return {
        "accuracy": float(round(accuracy, 4)),
        "balanced_accuracy": float(round(balanced_acc, 4)),
        "precision": float(round(precision, 4)),
        "recall": float(round(recall, 4)),
        "f1_score": float(round(f1, 4)),
        "roc_auc": float(round(roc_auc, 4)),
        "pr_auc": float(round(pr_auc, 4)),
        "brier_score": float(round(brier, 4)),
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp
        },
        "calibration_curve": calib_points
    }
