import asyncio
import pytest
from backend.app.api.endpoints import (
    health_check,
    get_model_info,
    analyze_chat,
    AnalyzeRequest,
    get_prediction_history,
    clear_prediction_history
)
from backend.app.schemas.chat import ChatMessage
from backend.app.services.chat_service import ChatService


def test_health_endpoint():
    res = asyncio.run(health_check())
    assert res["status"] == "healthy"
    assert res["app"] == "ReplySense"


def test_model_info_endpoint():
    res = asyncio.run(get_model_info())
    assert res.model_name is not None
    assert res.status in ["ready", "untrained"]


def test_chat_preview_whatsapp():
    sample_text = (
        "15/01/2024, 10:00 - UserA: Hey, are you free today?\n"
        "15/01/2024, 10:05 - UserB: Yes, what's up?\n"
        "15/01/2024, 10:06 - UserA: Can you review the draft?\n"
    )
    preview = ChatService.process_chat_upload(sample_text.encode("utf-8"), "chat.txt")
    assert preview.total_messages == 3
    assert len(preview.participants) == 2
    assert "UserA" in preview.participants
    assert "UserB" in preview.participants
    assert preview.default_sender == "UserA"


def test_analyze_endpoint():
    req = AnalyzeRequest(
        messages=[
            ChatMessage(id="1", timestamp="2024-01-01T10:00:00", sender="Alice", text="Hello Bob"),
            ChatMessage(id="2", timestamp="2024-01-01T10:15:00", sender="Bob", text="Hi Alice!"),
            ChatMessage(id="3", timestamp="2024-01-01T11:00:00", sender="Alice", text="Are you joining the sync?")
        ],
        sender="Alice",
        recipient="Bob",
        reply_horizon_hours=24.0
    )
    res = asyncio.run(analyze_chat(req))
    assert res.total_messages == 3
    assert res.sender_messages == 2
    assert res.recipient_messages == 1
    assert len(res.activity_by_hour) == 24
    assert len(res.activity_by_day) == 7


def test_history_workflow():
    clear_res = asyncio.run(clear_prediction_history())
    assert clear_res["status"] == "cleared"

    hist_res = asyncio.run(get_prediction_history(limit=50))
    assert hist_res.total_count == 0
