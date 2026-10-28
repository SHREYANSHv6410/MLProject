import os
import sys
import json
import logging
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.models.registry import registry
from scripts.train import build_dataset
from backend.app.models.evaluate import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate")


def run_evaluation():
    logger.info("Evaluating current ReplySense model artifact on benchmark dataset...")
    if not registry.is_ready():
        logger.error("No model artifact found. Please run 'python scripts/train.py' first.")
        sys.exit(1)

    X, y, groups, conv_count = build_dataset()
    logger.info("Running evaluation over %d instances...", len(X))

    model = registry.model
    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= 0.5).astype(int)

    metrics = evaluate_model(y, preds, probs)
    print("\n" + "=" * 50)
    print("      REPLYSENSE MODEL EVALUATION REPORT")
    print("=" * 50)
    print(f"Accuracy:          {metrics['accuracy']:.4f}")
    print(f"Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"Precision:         {metrics['precision']:.4f}")
    print(f"Recall:            {metrics['recall']:.4f}")
    print(f"F1 Score:          {metrics['f1_score']:.4f}")
    print(f"ROC-AUC:           {metrics['roc_auc']:.4f}")
    print(f"PR-AUC:            {metrics['pr_auc']:.4f}")
    print(f"Brier Score:       {metrics['brier_score']:.4f}")
    print("-" * 50)
    print(f"Confusion Matrix:  TN={metrics['confusion_matrix']['true_negatives']}, FP={metrics['confusion_matrix']['false_positives']}, FN={metrics['confusion_matrix']['false_negatives']}, TP={metrics['confusion_matrix']['true_positives']}")
    print("=" * 50 + "\n")
    return metrics


if __name__ == "__main__":
    run_evaluation()
