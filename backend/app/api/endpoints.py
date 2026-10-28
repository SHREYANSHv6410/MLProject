from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
import json
import time

from backend.app.schemas.chat import (
    ChatPreviewResponse,
    PredictRequest,
    ChatMessage
)
from backend.app.schemas.prediction import PredictionResult, ModelMetadata
from backend.app.schemas.analysis import ConversationStats
from backend.app.schemas.history import HistoryListResponse
from backend.app.services.chat_service import ChatService
from backend.app.services.prediction_service import PredictionService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.history_service import HistoryService
from backend.app.models.registry import registry
from backend.app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
START_TIME = time.time()


class AnalyzeRequest(BaseModel):
    messages: List[ChatMessage]
    sender: str
    recipient: str
    reply_horizon_hours: float = 24.0


@router.get("/health", tags=["System"])
async def health_check():
    """System health check and component operational status."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "model_loaded": registry.is_ready(),
        "history_enabled": settings.ENABLE_HISTORY
    }


@router.get("/model/info", response_model=ModelMetadata, tags=["Model"])
async def get_model_info():
    """Returns metadata, training parameters, documented limitations, and evaluation metrics."""
    if not registry.is_ready():
        return ModelMetadata(
            model_name="ReplySense-v1",
            algorithm="Calibrated HistGradientBoostingClassifier",
            trained_at="Not yet trained",
            dataset_info="Benchmark Conversational Corpus (train/val/test splits)",
            sample_count=0,
            conversation_count=0,
            target_horizon_hours=settings.DEFAULT_HORIZON_HOURS,
            is_calibrated=False,
            features_used=[],
            metrics={},
            limitations=[
                "Model artifact is not loaded on disk.",
                "Execute 'python scripts/train.py' to generate calibrated weights."
            ],
            status="untrained"
        )

    meta = registry.metadata or {}
    metrics = registry.evaluation_report or {}
    # flatten metrics if nested
    metric_values = {
        "accuracy": metrics.get("accuracy", 0.0),
        "balanced_accuracy": metrics.get("balanced_accuracy", 0.0),
        "precision": metrics.get("precision", 0.0),
        "recall": metrics.get("recall", 0.0),
        "f1_score": metrics.get("f1_score", 0.0),
        "roc_auc": metrics.get("roc_auc", 0.0),
        "pr_auc": metrics.get("pr_auc", 0.0),
        "brier_score": metrics.get("brier_score", 0.0)
    }

    return ModelMetadata(
        model_name=meta.get("model_name", "ReplySense-v1"),
        algorithm=meta.get("algorithm", "HistGradientBoostingClassifier (Calibrated)"),
        trained_at=meta.get("trained_at", "Unknown"),
        dataset_info=meta.get("dataset_info", "Conversational Reply Corpus"),
        sample_count=meta.get("sample_count", 0),
        conversation_count=meta.get("conversation_count", 0),
        target_horizon_hours=meta.get("target_horizon_hours", 24.0),
        is_calibrated=meta.get("is_calibrated", True),
        calibration_method=meta.get("calibration_method", "sigmoid"),
        features_used=meta.get("features_used", []),
        metrics=metric_values,
        limitations=meta.get("limitations", [
            "Predictions are statistical approximations based on chat timing and syntax.",
            "Does not account for private offline communication or third-party life events.",
            "Should not be construed as definitive intent or emotional state."
        ]),
        status="ready"
    )


@router.post("/chat/preview", response_model=ChatPreviewResponse, tags=["Chat"])
async def preview_chat_file(file: UploadFile = File(...)):
    """Upload and parse a conversation file (.txt WhatsApp export, .csv, or .json)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")

    try:
        preview = ChatService.process_chat_upload(content, file.filename)
        return preview
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error parsing chat export: {str(e)}")


@router.post("/predict", response_model=PredictionResult, tags=["Prediction"])
async def predict_reply(request: PredictRequest):
    """Generate calibrated reply probability and factor contributions for a target message."""
    return PredictionService.predict_reply(
        messages=request.messages,
        sender=request.sender,
        recipient=request.recipient,
        target_message_id=request.target_message_id,
        reply_horizon_hours=request.reply_horizon_hours
    )


@router.post("/analyze", response_model=ConversationStats, tags=["Analytics"])
async def analyze_chat(request: AnalyzeRequest):
    """Compute conversation messaging patterns, activity histograms, and response metrics."""
    return AnalyticsService.analyze_conversation(
        messages=request.messages,
        sender=request.sender,
        recipient=request.recipient,
        reply_horizon_hours=request.reply_horizon_hours
    )


@router.get("/history", response_model=HistoryListResponse, tags=["History"])
async def get_prediction_history(limit: int = 50):
    """Retrieve local session prediction history if enabled."""
    return HistoryService.list_history(limit=limit)


@router.delete("/history", tags=["History"])
async def clear_prediction_history():
    """Purge local prediction history database."""
    success = HistoryService.purge_history()
    return {"status": "cleared" if success else "failed"}
