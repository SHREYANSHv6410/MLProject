from datetime import datetime, timedelta
import pytest
from backend.app.schemas.chat import ChatMessage
from backend.app.features.extractor import FeatureExtractor
from backend.app.features.schema import FEATURE_COLUMNS


def test_feature_extraction_completeness():
    t0 = datetime(2024, 1, 1, 14, 0, 0)
    messages = [
        ChatMessage(id="m1", timestamp=t0, sender="Alice", text="Hey Bob, can you please call me? 😊"),
        ChatMessage(id="m2", timestamp=t0 + timedelta(minutes=10), sender="Bob", text="Yes, calling in a sec!"),
        ChatMessage(id="m3", timestamp=t0 + timedelta(minutes=40), sender="Alice", text="Did you check https://example.com? What do you think?")
    ]

    extractor = FeatureExtractor(reply_horizon_hours=24.0)
    feat = extractor.extract_features_for_message(messages, target_idx=2, sender="Alice", recipient="Bob")

    # Check all columns exist
    for col in FEATURE_COLUMNS:
        assert col in feat, f"Missing feature column: {col}"

    # Check linguistic features on target message
    assert feat["is_question"] == 1
    assert feat["question_mark_count"] == 2
    assert feat["has_url"] == 1
    assert feat["hour_of_day"] == 14
    assert feat["previous_messages_count"] == 2
    assert feat["sender_message_count"] == 1
    assert feat["recipient_message_count"] == 1
    assert feat["consecutive_unanswered_sender"] == 0  # previous message was from Bob!
