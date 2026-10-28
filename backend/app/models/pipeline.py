from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd

# Check sklearn availability
try:
    import sklearn
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.calibration import CalibratedClassifierCV
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class NumPyStandardScaler:
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        X_arr = np.asarray(X, dtype=float)
        self.mean_ = np.nanmean(X_arr, axis=0)
        self.scale_ = np.nanstd(X_arr, axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X):
        X_arr = np.asarray(X, dtype=float)
        return (X_arr - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class NumPyLogisticRegression:
    """Logistic regression with L2 regularization and gradient descent."""
    def __init__(self, lr: float = 0.05, reg: float = 0.1, n_iter: int = 400):
        self.lr = lr
        self.reg = reg
        self.n_iter = n_iter
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y):
        X_arr = np.asarray(X, dtype=float)
        y_arr = np.asarray(y, dtype=float)
        n_samples, n_features = X_arr.shape

        self.weights = np.zeros(n_features)
        self.bias = 0.0

        for _ in range(self.n_iter):
            linear_model = np.dot(X_arr, self.weights) + self.bias
            linear_clamped = np.clip(linear_model, -30, 30)
            y_pred = 1.0 / (1.0 + np.exp(-linear_clamped))

            dw = (1.0 / n_samples) * np.dot(X_arr.T, (y_pred - y_arr)) + (self.reg / n_samples) * self.weights
            db = (1.0 / n_samples) * np.sum(y_pred - y_arr)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db
        return self

    def predict_proba(self, X):
        X_arr = np.asarray(X, dtype=float)
        linear_model = np.dot(X_arr, self.weights) + self.bias
        linear_clamped = np.clip(linear_model, -30, 30)
        prob_pos = 1.0 / (1.0 + np.exp(-linear_clamped))
        prob_neg = 1.0 - prob_pos
        return np.column_stack([prob_neg, prob_pos])


class DecisionStump:
    """One-level decision tree splitting on feature j with threshold theta."""
    def __init__(self):
        self.polarity = 1
        self.feature_idx = None
        self.threshold = None

    def predict(self, X):
        n_samples = X.shape[0]
        X_column = X[:, self.feature_idx]
        predictions = np.ones(n_samples)
        if self.polarity == 1:
            predictions[X_column < self.threshold] = -1
        else:
            predictions[X_column > self.threshold] = -1
        return predictions


class NumPyGradientBoostingClassifier:
    """Ensemble of decision stumps boosting pseudo-residuals."""
    def __init__(self, n_estimators: int = 40, learning_rate: float = 0.1):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.stumps = []
        self.base_pred = 0.0

    def fit(self, X, y):
        X_arr = np.asarray(X, dtype=float)
        y_arr = np.asarray(y, dtype=float)
        n_samples, n_features = X_arr.shape

        mean_y = np.clip(np.mean(y_arr), 1e-4, 1.0 - 1e-4)
        self.base_pred = np.log(mean_y / (1.0 - mean_y))
        raw_preds = np.full(n_samples, self.base_pred)

        for _ in range(self.n_estimators):
            probs = 1.0 / (1.0 + np.exp(-np.clip(raw_preds, -30, 30)))
            residuals = y_arr - probs

            stump = DecisionStump()
            min_error = float("inf")

            for feat_i in range(n_features):
                X_col = X_arr[:, feat_i]
                thresholds = np.unique(X_col)
                if len(thresholds) > 15:
                    thresholds = np.percentile(thresholds, np.linspace(5, 95, 12))

                for threshold in thresholds:
                    for polarity in [1, -1]:
                        preds = np.ones(n_samples)
                        if polarity == 1:
                            preds[X_col < threshold] = -1
                        else:
                            preds[X_col > threshold] = -1

                        error = np.sum((residuals - preds * self.learning_rate) ** 2)
                        if error < min_error:
                            min_error = error
                            stump.polarity = polarity
                            stump.threshold = threshold
                            stump.feature_idx = feat_i

            stump_preds = stump.predict(X_arr)
            raw_preds += self.learning_rate * stump_preds
            self.stumps.append(stump)
        return self

    def predict_proba(self, X):
        X_arr = np.asarray(X, dtype=float)
        raw_preds = np.full(X_arr.shape[0], self.base_pred)
        for stump in self.stumps:
            raw_preds += self.learning_rate * stump.predict(X_arr)
        prob_pos = 1.0 / (1.0 + np.exp(-np.clip(raw_preds, -30, 30)))
        prob_neg = 1.0 - prob_pos
        return np.column_stack([prob_neg, prob_pos])


class CalibratedModelWrapper:
    """Wrapper providing feature normalization and Platt scaling calibration."""
    def __init__(self, base_estimator, method: str = "sigmoid"):
        self.scaler = NumPyStandardScaler()
        self.base_estimator = base_estimator
        self.method = method
        self.calibrator = None

    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        self.base_estimator.fit(X_scaled, y)
        raw_probs = self.base_estimator.predict_proba(X_scaled)[:, 1]

        logit = np.log(np.clip(raw_probs, 1e-4, 1.0 - 1e-4) / (1.0 - np.clip(raw_probs, 1e-4, 1.0 - 1e-4)))
        self.calibrator = NumPyLogisticRegression(lr=0.1, reg=0.01, n_iter=200)
        self.calibrator.fit(logit.reshape(-1, 1), y)
        return self

    def predict_proba(self, X):
        X_scaled = self.scaler.transform(X)
        raw_probs = self.base_estimator.predict_proba(X_scaled)[:, 1]
        logit = np.log(np.clip(raw_probs, 1e-4, 1.0 - 1e-4) / (1.0 - np.clip(raw_probs, 1e-4, 1.0 - 1e-4)))
        return self.calibrator.predict_proba(logit.reshape(-1, 1))


def build_candidate_pipelines() -> Dict[str, Any]:
    if SKLEARN_AVAILABLE:
        return {
            "hist_gradient_boosting": HistGradientBoostingClassifier(
                max_iter=100, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=15, random_state=42
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=8, min_samples_split=5, min_samples_leaf=3, class_weight="balanced", random_state=42
            ),
            "logistic_regression": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced", random_state=42))
            ])
        }
    else:
        return {
            "hist_gradient_boosting": NumPyGradientBoostingClassifier(n_estimators=30, learning_rate=0.08),
            "random_forest": NumPyGradientBoostingClassifier(n_estimators=25, learning_rate=0.10),
            "logistic_regression": NumPyLogisticRegression(lr=0.05, reg=0.1, n_iter=300)
        }


def build_calibrated_model(base_estimator, method: str = "sigmoid", cv: int = 3):
    if SKLEARN_AVAILABLE:
        return CalibratedClassifierCV(estimator=base_estimator, method=method, cv=cv)
    else:
        return CalibratedModelWrapper(base_estimator=base_estimator, method=method)
