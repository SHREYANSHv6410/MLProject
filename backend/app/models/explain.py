from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.schemas.prediction import FactorContribution
from backend.app.features.schema import FEATURE_COLUMNS, FEATURE_DISPLAY_NAMES, FEATURE_DESCRIPTIONS


class ModelExplainer:
    """
    Computes grounded feature contributions and human-interpretable explanations.
    Uses marginal perturbation analysis against training baseline distribution.
    """

    def __init__(self, model, baseline_means: Dict[str, float], baseline_stds: Dict[str, float]):
        self.model = model
        self.baseline_means = baseline_means
        self.baseline_stds = baseline_stds

    def explain_instance(
        self,
        feature_dict: Dict[str, Any],
        predicted_prob: float,
        top_k: int = 6
    ) -> List[FactorContribution]:
        contributions: List[FactorContribution] = []

        # Base probability when features are at average
        base_df = pd.DataFrame([{col: self.baseline_means.get(col, 0.0) for col in FEATURE_COLUMNS}])
        try:
            base_prob = float(self.model.predict_proba(base_df)[0][1])
        except Exception:
            base_prob = 0.50

        # Create single row df for target instance
        target_df = pd.DataFrame([{col: feature_dict.get(col, 0.0) for col in FEATURE_COLUMNS}])

        # Individual feature marginal contribution
        raw_contributions = []
        for col in FEATURE_COLUMNS:
            val = feature_dict.get(col, 0.0)
            mean_val = self.baseline_means.get(col, 0.0)
            std_val = self.baseline_stds.get(col, 1.0) or 1.0

            # Perturb feature back to baseline mean
            perturbed_df = target_df.copy()
            perturbed_df[col] = mean_val
            try:
                prob_without_feature = float(self.model.predict_proba(perturbed_df)[0][1])
                # Delta indicates how much this specific feature moved probability from the counterfactual
                delta = predicted_prob - prob_without_feature
            except Exception:
                delta = 0.0

            raw_contributions.append((col, val, delta, mean_val, std_val))

        # Sort by absolute impact
        raw_contributions.sort(key=lambda x: abs(x[2]), reverse=True)

        for col, val, delta, mean_val, std_val in raw_contributions[:top_k]:
            abs_delta = abs(delta)
            if abs_delta >= 0.08:
                impact = "high"
            elif abs_delta >= 0.03:
                impact = "medium"
            elif abs_delta >= 0.01:
                impact = "low"
            else:
                impact = "negligible"

            if delta > 0.005:
                direction = "increases_reply_probability"
            elif delta < -0.005:
                direction = "decreases_reply_probability"
            else:
                direction = "neutral"

            display_name = FEATURE_DISPLAY_NAMES.get(col, col.replace("_", " ").title())
            desc = self._generate_explanation(col, val, delta, mean_val)

            contributions.append(FactorContribution(
                feature=col,
                display_name=display_name,
                value=val,
                contribution=float(round(delta, 4)),
                direction=direction,
                impact=impact,
                description=desc
            ))

        return contributions

    def _generate_explanation(self, col: str, val: Any, delta: float, mean_val: float) -> str:
        if col == "historical_reply_rate":
            rate_pct = int(round(float(val) * 100))
            if delta > 0:
                return f"Strong conversational rapport ({rate_pct}% prior response rate) heavily boosts reply likelihood."
            return f"Low historical response rate ({rate_pct}%) suggests historically infrequent replies in this chat."

        if col == "is_question":
            if val == 1:
                return "Message is phrased as a question, which directly prompts a conversational answer."
            return "Message does not contain a question mark or clear inquiry, reducing conversational pressure."

        if col == "is_recipient_active_hour":
            if val == 1:
                return "Sent during hours when the recipient is historically most active and responsive."
            return "Sent outside the recipient's typical active messaging window."

        if col == "consecutive_unanswered_sender":
            if val > 1:
                return f"Multiple prior messages ({val}) sent in a row without an incoming reply can cause recipient fatigue."
            return "First message in this turn, maintaining normal conversational pacing."

        if col == "minutes_since_last_incoming":
            mins = float(val)
            if mins < 30:
                return f"Sent just {int(mins)} minutes after recipient's last message, catching active conversation momentum."
            elif mins > 1440:
                return "Sent over 24 hours after the last incoming message, where conversational context is cold."
            return f"{int(mins // 60)} hours since recipient's last message."

        if col == "has_request_cue":
            if val == 1:
                return "Contains an explicit action cue (e.g. 'please', 'let me know', 'call me') prompting prompt attention."
            return "Does not include explicit request phrases."

        if col == "message_length":
            if val > 200:
                return f"Long message ({val} chars) requires more effort or reading time to address."
            elif val < 20:
                return "Short, concise message, which is quick to digest."
            return f"Moderate message length ({val} characters)."

        if col == "is_weekend":
            if val == 1:
                return "Sent on a weekend, which may change personal or work responsiveness."
            return "Sent on a weekday during standard scheduling."

        # Default fallback
        base_desc = FEATURE_DESCRIPTIONS.get(col, "Influences response dynamics based on learned patterns.")
        return f"{base_desc} (Current: {val})"
