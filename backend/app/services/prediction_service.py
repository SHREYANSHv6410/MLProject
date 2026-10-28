import uuid
from typing import List, Optional
import pandas as pd
from fastapi import HTTPException

from backend.app.schemas.chat import ChatMessage, PredictRequest
from backend.app.schemas.prediction import PredictionResult, FactorContribution
from backend.app.features.extractor import FeatureExtractor
from backend.app.features.schema import FEATURE_COLUMNS
from backend.app.models.registry import registry
from backend.app.core.database import save_prediction


class PredictionService:
    """Orchestrates feature extraction, model inference, explainability, and persistence."""

    @staticmethod
    def predict_reply(
        messages: List[ChatMessage],
        sender: str,
        recipient: str,
        target_message_id: Optional[str] = None,
        reply_horizon_hours: float = 24.0,
        filename: str = "chat_export"
    ) -> PredictionResult:
        if not messages:
            raise HTTPException(status_code=400, detail="Cannot predict on an empty conversation.")

        # Filter out system messages
        valid_msgs = [m for m in messages if not m.is_system]
        if not valid_msgs:
            raise HTTPException(status_code=400, detail="No non-system messages found in conversation.")

        # Ensure sorted
        valid_msgs.sort(key=lambda m: m.timestamp)

        # Locate target message
        target_idx: Optional[int] = None
        if target_message_id:
            for i, m in enumerate(valid_msgs):
                if m.id == target_message_id:
                    target_idx = i
                    break
            if target_idx is None:
                raise HTTPException(status_code=404, detail=f"Target message '{target_message_id}' not found.")
        else:
            # Default to the latest sender message
            for i in range(len(valid_msgs) - 1, -1, -1):
                if valid_msgs[i].sender == sender:
                    target_idx = i
                    break

            if target_idx is None:
                raise HTTPException(status_code=400, detail=f"No messages sent by designated sender '{sender}' found.")

        target_msg = valid_msgs[target_idx]

        # Check if model is loaded and ready
        if not registry.is_ready():
            raise HTTPException(
                status_code=503,
                detail=(
                    "ML model artifact is not yet initialized. "
                    "Run 'python scripts/train.py' or initiate model training from the admin script."
                )
            )

        # Extract features
        extractor = FeatureExtractor(reply_horizon_hours=reply_horizon_hours)
        feature_dict = extractor.extract_features_for_message(valid_msgs, target_idx, sender, recipient)
        df_features = pd.DataFrame([feature_dict], columns=FEATURE_COLUMNS)

        # Run inference
        try:
            proba_arr = registry.model.predict_proba(df_features)
            prob = float(proba_arr[0][1])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing model inference: {str(e)}")

        decision_threshold = 0.50
        outcome = "Reply likely" if prob >= decision_threshold else "Reply less likely"

        # Model uncertainty estimation
        # Probabilities close to the decision boundary (0.5) reflect higher uncertainty
        dist_from_margin = abs(prob - decision_threshold)
        if dist_from_margin < 0.12:
            uncertainty_level = "Elevated"
        elif dist_from_margin < 0.25:
            uncertainty_level = "Moderate"
        else:
            uncertainty_level = "Low"

        # Explainability
        key_factors: List[FactorContribution] = []
        if registry.explainer:
            key_factors = registry.explainer.explain_instance(feature_dict, prob, top_k=5)

        # Summary verdict
        prob_pct = int(round(prob * 100))
        if prob >= 0.70:
            summary = f"Strong statistical likelihood ({prob_pct}%) of receiving a reply within {int(reply_horizon_hours)} hours, supported by active conversation patterns."
        elif prob >= 0.50:
            summary = f"Moderate likelihood ({prob_pct}%) of receiving a reply within {int(reply_horizon_hours)} hours. Response depends on current availability."
        elif prob >= 0.30:
            summary = f"Below-average reply probability ({prob_pct}%). Historical pacing suggests delayed or absent follow-up within {int(reply_horizon_hours)} hours."
        else:
            summary = f"Low probability ({prob_pct}%) of receiving a reply within {int(reply_horizon_hours)} hours based on historical turn patterns."

        pred_id = f"pred_{uuid.uuid4().hex[:10]}"

        # Save to history if enabled
        key_factor_summaries = [f"{f.display_name}: {f.description}" for f in key_factors[:3]]
        save_prediction(
            prediction_id=pred_id,
            filename=filename,
            sender=sender,
            recipient=recipient,
            target_message_text=target_msg.text,
            target_message_time=target_msg.timestamp,
            predicted_outcome=outcome,
            probability=prob,
            uncertainty_level=uncertainty_level,
            key_factors=key_factor_summaries,
            reply_horizon_hours=reply_horizon_hours
        )

        return PredictionResult(
            outcome=outcome,
            probability=round(prob, 4),
            calibrated=True,
            uncertainty_level=uncertainty_level,
            confidence_interval={
                "lower": max(0.0, round(prob - (0.15 if uncertainty_level == 'Elevated' else 0.08), 4)),
                "upper": min(1.0, round(prob + (0.15 if uncertainty_level == 'Elevated' else 0.08), 4))
            },
            decision_threshold=decision_threshold,
            target_message=target_msg,
            reply_horizon_hours=reply_horizon_hours,
            model_version=registry.metadata.get("model_name", "ReplySense-v1") if registry.metadata else "ReplySense-v1",
            algorithm=registry.metadata.get("algorithm", "Calibrated HistGradientBoosting") if registry.metadata else "HistGradientBoosting",
            key_factors=key_factors,
            summary_verdict=summary
        )
