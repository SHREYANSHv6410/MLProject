import pytest
import numpy as np
import pandas as pd
from backend.app.models.evaluate import evaluate_model
from backend.app.models.pipeline import build_candidate_pipelines, build_calibrated_model
from backend.app.features.schema import FEATURE_COLUMNS
from backend.app.models.explain import ModelExplainer


def test_evaluate_model_metrics():
    y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.65, 0.35, 0.2, 0.75, 0.4])
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = evaluate_model(y_true, y_pred, y_prob)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["brier_score"] <= 1.0
    assert "confusion_matrix" in metrics
    assert metrics["confusion_matrix"]["true_positives"] == 4


def test_model_pipeline_and_calibration():
    # Synthetic small dataset
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(50, len(FEATURE_COLUMNS)), columns=FEATURE_COLUMNS)
    y = np.random.randint(0, 2, size=50)

    pipelines = build_candidate_pipelines()
    rf = pipelines["random_forest"]
    calibrated = build_calibrated_model(rf, method="sigmoid", cv=2)
    calibrated.fit(X, y)

    probs = calibrated.predict_proba(X)[:, 1]
    assert len(probs) == 50
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)


def test_model_explainer():
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(30, len(FEATURE_COLUMNS)), columns=FEATURE_COLUMNS)
    y = np.random.randint(0, 2, size=30)

    pipelines = build_candidate_pipelines()
    clf = pipelines["random_forest"]
    clf.fit(X, y)

    means = X.mean().to_dict()
    stds = X.std().to_dict()
    explainer = ModelExplainer(clf, means, stds)

    sample_feat = {col: 1.0 for col in FEATURE_COLUMNS}
    contributions = explainer.explain_instance(sample_feat, predicted_prob=0.8, top_k=5)

    assert len(contributions) == 5
    for c in contributions:
        assert c.feature in FEATURE_COLUMNS
        assert c.direction in ["increases_reply_probability", "decreases_reply_probability", "neutral"]
