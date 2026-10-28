from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.prediction import PredictionResult


class HistoryRecord(BaseModel):
    id: str
    created_at: datetime
    filename: str
    sender: str
    recipient: str
    target_message_text: str
    target_message_time: datetime
    predicted_outcome: str
    probability: float
    uncertainty_level: str
    key_factors_summary: List[str]
    reply_horizon_hours: float


class HistoryListResponse(BaseModel):
    enabled: bool
    total_count: int
    items: List[HistoryRecord]
