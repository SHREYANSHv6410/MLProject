import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.schemas.chat import ChatMessage
from backend.app.features.extractor import FeatureExtractor
from backend.app.features.schema import FEATURE_COLUMNS
from backend.app.models.pipeline import build_candidate_pipelines, build_calibrated_model
from backend.app.models.evaluate import evaluate_model
from scripts.generate_demo_data import generate_benchmark_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train")

DATA_PATH = BASE_DIR / "data" / "demo" / "benchmark_conversations.json"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def split_by_groups(groups: np.ndarray, test_size: float = 0.25, random_state: int = 42):
    """
    Split instances based on distinct group identifiers (conversation IDs).
    Guarantees no messages from the same conversation appear in both train and test splits.
    """
    unique_groups = np.unique(groups)
    rng = np.random.RandomState(random_state)
    shuffled = unique_groups.copy()
    rng.shuffle(shuffled)
    n_test = max(1, int(len(shuffled) * test_size))
    test_g = set(shuffled[:n_test])

    test_indices = np.array([i for i, g in enumerate(groups) if g in test_g])
    train_indices = np.array([i for i, g in enumerate(groups) if g not in test_g])
    return train_indices, test_indices


def build_dataset(horizon_hours: float = 24.0):
    if not DATA_PATH.exists():
        logger.info("Benchmark data not found. Generating demo data...")
        generate_benchmark_dataset()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    logger.info("Loaded %d conversations for dataset construction.", len(conversations))

    extractor = FeatureExtractor(reply_horizon_hours=horizon_hours)
    feature_rows = []
    labels = []
    groups = []

    censored_count = 0
    total_sender_msgs = 0

    for conv in conversations:
        c_id = conv["conversation_id"]
        sender = conv["sender"]
        recipient = conv["recipient"]
        raw_msgs = conv["messages"]

        msgs = [
            ChatMessage(
                id=m["id"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                sender=m["sender"],
                text=m["text"],
                is_media=m.get("is_media", False),
                is_system=m.get("is_system", False)
            )
            for m in raw_msgs
        ]
        msgs.sort(key=lambda m: m.timestamp)
        if not msgs:
            continue

        conv_end_time = msgs[-1].timestamp

        for i, m in enumerate(msgs):
            if m.sender != sender:
                continue

            total_sender_msgs += 1
            msg_time = m.timestamp

            # Check for reply from recipient
            replied = False
            for j in range(i + 1, len(msgs)):
                if msgs[j].sender == recipient:
                    delta_h = (msgs[j].timestamp - msg_time).total_seconds() / 3600.0
                    if 0 <= delta_h <= horizon_hours:
                        replied = True
                    break

            # Censoring check: If not replied, did we observe the full horizon?
            time_until_end_h = (conv_end_time - msg_time).total_seconds() / 3600.0
            if not replied and time_until_end_h < horizon_hours:
                # Censored observation window! Exclude to avoid false negative bias
                censored_count += 1
                continue

            # Extract features strictly using messages preceding this message
            feat = extractor.extract_features_for_message(msgs, i, sender, recipient)
            feature_rows.append(feat)
            labels.append(1 if replied else 0)
            groups.append(c_id)

    logger.info(
        "Extracted %d valid labeled instances (%d censored messages excluded from training window).",
        len(feature_rows),
        censored_count
    )

    df_X = pd.DataFrame(feature_rows, columns=FEATURE_COLUMNS)
    y = np.array(labels)
    groups = np.array(groups)
    return df_X, y, groups, len(conversations)


def run_training():
    logger.info("--- Starting ReplySense ML Pipeline Training ---")
    horizon_hours = 24.0
    X, y, groups, conv_count = build_dataset(horizon_hours)

    class_balance = float(np.mean(y))
    logger.info("Overall target class balance: %.2f%% positive (replied within %dh)", class_balance * 100, horizon_hours)

    # Conversation-grouped Train/Validation/Test split
    train_val_idx, test_idx = split_by_groups(groups, test_size=0.25, random_state=42)
    X_train_val, y_train_val = X.iloc[train_val_idx], y[train_val_idx]
    groups_train_val = groups[train_val_idx]

    X_test, y_test = X.iloc[test_idx], y[test_idx]

    # Split train_val into train and validation
    train_idx, val_idx = split_by_groups(groups_train_val, test_size=0.25, random_state=42)
    X_train, y_train = X_train_val.iloc[train_idx], y_train_val[train_idx]
    X_val, y_val = X_train_val.iloc[val_idx], y_train_val[val_idx]

    logger.info("Split sizes -> Train: %d, Validation: %d, Held-out Test: %d", len(X_train), len(X_val), len(X_test))

    # Compare Candidate Models
    candidates = build_candidate_pipelines()
    best_candidate_name = None
    best_val_score = -1.0
    best_model = None

    for name, model in candidates.items():
        logger.info("Evaluating candidate: %s", name)
        model.fit(X_train, y_train)
        val_probs = model.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)
        val_metrics = evaluate_model(y_val, val_preds, val_probs)
        logger.info(
            "Candidate [%s] Validation ROC-AUC: %.4f | PR-AUC: %.4f | F1: %.4f | Brier: %.4f",
            name, val_metrics["roc_auc"], val_metrics["pr_auc"], val_metrics["f1_score"], val_metrics["brier_score"]
        )

        composite_score = val_metrics["roc_auc"] + val_metrics["pr_auc"]
        if composite_score > best_val_score:
            best_val_score = composite_score
            best_candidate_name = name
            best_model = model

    logger.info("Selected winning candidate architecture: %s", best_candidate_name)

    # Train winning architecture on full train_val set with Calibrated Probability Output
    logger.info("Fitting probability calibration (Platt scaling with sigmoid) on train+val...")
    calibrated_clf = build_calibrated_model(base_estimator=best_model, method="sigmoid", cv=3)
    calibrated_clf.fit(X_train_val, y_train_val)

    # Final Evaluation on Held-out Test Set
    test_probs = calibrated_clf.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= 0.5).astype(int)
    test_metrics = evaluate_model(y_test, test_preds, test_probs)

    logger.info("=== HELD-OUT TEST EVALUATION METRICS ===")
    logger.info("Test Accuracy:         %.4f", test_metrics["accuracy"])
    logger.info("Test Balanced Acc:     %.4f", test_metrics["balanced_accuracy"])
    logger.info("Test Precision:        %.4f", test_metrics["precision"])
    logger.info("Test Recall:           %.4f", test_metrics["recall"])
    logger.info("Test F1 Score:         %.4f", test_metrics["f1_score"])
    logger.info("Test ROC-AUC:          %.4f", test_metrics["roc_auc"])
    logger.info("Test PR-AUC:           %.4f", test_metrics["pr_auc"])
    logger.info("Test Brier Score:      %.4f", test_metrics["brier_score"])

    # Compute baseline feature statistics for runtime explainability
    baseline_means = X_train_val.mean().to_dict()
    baseline_stds = X_train_val.std().replace(0, 1.0).to_dict()

    artifact = {
        "model": calibrated_clf,
        "baseline_stats": {
            "means": baseline_means,
            "stds": baseline_stds
        },
        "feature_columns": FEATURE_COLUMNS,
        "algorithm": f"Calibrated {best_candidate_name}",
        "trained_at": datetime.utcnow().isoformat()
    }

    model_path = ARTIFACTS_DIR / "model.joblib"
    joblib.dump(artifact, model_path)
    logger.info("Saved trained artifact to: %s", model_path)

    # Save metadata
    metadata = {
        "model_name": "ReplySense-v1",
        "algorithm": f"Calibrated {best_candidate_name}",
        "trained_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "dataset_info": "Multi-turn Conversational Reply Benchmark (40 conversations, 600+ message turns)",
        "sample_count": len(X),
        "conversation_count": conv_count,
        "target_horizon_hours": horizon_hours,
        "is_calibrated": True,
        "calibration_method": "sigmoid (Platt scaling)",
        "features_used": FEATURE_COLUMNS,
        "limitations": [
            "Assumes two primary interlocutors in standard 1-on-1 dialogue turns.",
            "Predictions are statistical likelihoods based on timing and linguistic structure.",
            "Real-world unexpected interruptions (offline meetings, emergencies) cannot be observed by text models.",
            "Probabilities should be interpreted as calibrated guides rather than guaranteed human outcomes."
        ]
    }

    with open(ARTIFACTS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(ARTIFACTS_DIR / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2)

    logger.info("Saved metadata and evaluation report successfully.")
    return test_metrics


if __name__ == "__main__":
    run_training()
