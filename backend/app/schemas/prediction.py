from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from backend.app.schemas.chat import ChatMessage


class FactorContribution(BaseModel):
    feature: str
    display_name: str
    value: Any
    contribution: float
    direction: Literal["increases_reply_probability", "decreases_reply_probability", "neutral"]
    impact: Literal["high", "medium", "low", "negligible"]
    description: str


class PredictionResult(BaseModel):
    outcome: Literal["Reply likely", "Reply less likely"]
    probability: float = Field(..., description="Estimated probability of receiving a reply within the horizon")
    calibrated: bool = Field(default=True, description="Whether probability is calibrated via Platt scaling / Isotonic regression")
    uncertainty_level: Literal["Low", "Moderate", "Elevated"]
    confidence_interval: Optional[Dict[str, float]] = None
    decision_threshold: float = 0.5
    target_message: ChatMessage
    reply_horizon_hours: float
    model_version: str
    algorithm: str
    key_factors: List[FactorContribution]
    summary_verdict: str
    disclaimer: str = (
        "ReplySense estimates statistical response likelihood based on historical message patterns. "
        "Human communication is influenced by unobservable real-world factors; predictions are probabilistic and not guarantees."
    )


class ModelMetadata(BaseModel):
    model_name: str
    algorithm: str
    trained_at: str
    dataset_info: str
    sample_count: int
    conversation_count: int
    target_horizon_hours: float
    is_calibrated: bool
    calibration_method: Optional[str] = None
    features_used: List[str]
    metrics: Dict[str, float]
    limitations: List[str]
    status: Literal["ready", "untrained", "degraded"]
