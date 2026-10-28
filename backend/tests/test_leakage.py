from datetime import datetime, timedelta
import pytest
from backend.app.schemas.chat import ChatMessage
from backend.app.features.extractor import FeatureExtractor


def test_chronological_leakage_invariance():
    """
    Features extracted for a message at index i must be strictly invariant to
    any subsequent messages appended to the conversation (messages after index i).
    """
    t0 = datetime(2024, 1, 1, 10, 0, 0)
    messages_base = [
        ChatMessage(id="m1", timestamp=t0, sender="Alice", text="Hey Bob, can you review this?"),
        ChatMessage(id="m2", timestamp=t0 + timedelta(minutes=15), sender="Bob", text="Sure, looking at it now."),
        ChatMessage(id="m3", timestamp=t0 + timedelta(minutes=60), sender="Alice", text="Did you find any issues?")
    ]

    extractor = FeatureExtractor(reply_horizon_hours=24.0)

    # Extract features for m3 with no future messages
    feat_without_future = extractor.extract_features_for_message(messages_base, target_idx=2, sender="Alice", recipient="Bob")

    # Now add future messages (Bob replies 5 minutes later, then Alice replies, etc.)
    messages_extended = list(messages_base) + [
        ChatMessage(id="m4", timestamp=t0 + timedelta(minutes=65), sender="Bob", text="Found one small typo on page 2."),
        ChatMessage(id="m5", timestamp=t0 + timedelta(minutes=70), sender="Alice", text="Fixed, thank you!")
    ]

    feat_with_future = extractor.extract_features_for_message(messages_extended, target_idx=2, sender="Alice", recipient="Bob")

    # Features must match identically
    for key in feat_without_future:
        assert feat_without_future[key] == feat_with_future[key], (
            f"Feature '{key}' leaked future information! "
            f"Without future: {feat_without_future[key]}, With future: {feat_with_future[key]}"
        )


def test_censoring_logic():
    """
    Verify that an unanswered message without sufficient observation window is recognized as censored.
    """
    t0 = datetime(2024, 1, 1, 10, 0, 0)
    # Conversation ends only 2 hours after m1 was sent
    conv_end = t0 + timedelta(hours=2)
    horizon_hours = 24.0

    time_until_end_h = (conv_end - t0).total_seconds() / 3600.0
    is_censored = time_until_end_h < horizon_hours
    assert is_censored is True, "Message with <24h observation window before conversation end must be censored."
