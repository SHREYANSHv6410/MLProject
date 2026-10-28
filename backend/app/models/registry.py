import json
import joblib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.models.explain import ModelExplainer


class ModelRegistry:
    """Manages model artifact persistence, loading, and runtime explainer caching."""

    def __init__(self):
        self._model = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._evaluation_report: Optional[Dict[str, Any]] = None
        self._explainer: Optional[ModelExplainer] = None
        self._baseline_stats: Optional[Dict[str, Any]] = None

    def is_ready(self) -> bool:
        return settings.MODEL_PATH.exists() and settings.METADATA_PATH.exists()

    def load(self, force_reload: bool = False):
        if self._model is not None and not force_reload:
            return

        if not self.is_ready():
            return

        try:
            artifact = joblib.load(settings.MODEL_PATH)
            if isinstance(artifact, dict):
                self._model = artifact.get("model")
                self._baseline_stats = artifact.get("baseline_stats", {})
            else:
                self._model = artifact
                self._baseline_stats = {}

            with open(settings.METADATA_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)

            if settings.METRICS_PATH.exists():
                with open(settings.METRICS_PATH, "r", encoding="utf-8") as f:
                    self._evaluation_report = json.load(f)

            # Initialize explainer
            means = self._baseline_stats.get("means", {}) if self._baseline_stats else {}
            stds = self._baseline_stats.get("stds", {}) if self._baseline_stats else {}
            self._explainer = ModelExplainer(self._model, means, stds)

        except Exception as e:
            self._model = None
            self._metadata = None
            raise RuntimeError(f"Failed to load model artifact: {str(e)}")

    @property
    def model(self):
        if self._model is None:
            self.load()
        return self._model

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        if self._metadata is None:
            self.load()
        return self._metadata

    @property
    def evaluation_report(self) -> Optional[Dict[str, Any]]:
        if self._evaluation_report is None:
            self.load()
        return self._evaluation_report

    @property
    def explainer(self) -> Optional[ModelExplainer]:
        if self._explainer is None:
            self.load()
        return self._explainer


registry = ModelRegistry()
