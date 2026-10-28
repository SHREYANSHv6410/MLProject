from typing import List, Dict, Any

FEATURE_COLUMNS = [
    # Message-level features
    "message_length",
    "word_count",
    "question_mark_count",
    "is_question",
    "has_request_cue",
    "emoji_count",
    "exclamation_count",
    "uppercase_ratio",
    "has_url",
    "is_media",
    # Conversation-level features
    "historical_reply_rate",
    "previous_messages_count",
    "sender_message_count",
    "recipient_message_count",
    "sender_recipient_ratio",
    "consecutive_unanswered_sender",
    "avg_response_time_minutes",
    "median_response_time_minutes",
    "minutes_since_last_incoming",
    # Temporal features
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_recipient_active_hour",
]

FEATURE_DISPLAY_NAMES = {
    "message_length": "Message Length",
    "word_count": "Word Count",
    "question_mark_count": "Question Marks",
    "is_question": "Direct Question Asked",
    "has_request_cue": "Contains Request / Action Cue",
    "emoji_count": "Emoji Count",
    "exclamation_count": "Exclamation Marks",
    "uppercase_ratio": "Uppercase Ratio (Emphasis)",
    "has_url": "Contains Link / URL",
    "is_media": "Contains Attachment / Media",
    "historical_reply_rate": "Historical Reply Rate",
    "previous_messages_count": "Conversation Depth (Total Prior Messages)",
    "sender_message_count": "Prior Sender Messages",
    "recipient_message_count": "Prior Recipient Messages",
    "sender_recipient_ratio": "Sender-to-Recipient Ratio",
    "consecutive_unanswered_sender": "Consecutive Sender Messages (Double Texting)",
    "avg_response_time_minutes": "Historical Avg Response Time (min)",
    "median_response_time_minutes": "Historical Median Response Time (min)",
    "minutes_since_last_incoming": "Time Since Last Recipient Message (min)",
    "hour_of_day": "Hour of Day Sent",
    "day_of_week": "Day of Week",
    "is_weekend": "Sent on Weekend",
    "is_recipient_active_hour": "Sent During Recipient Active Hours"
}

FEATURE_DESCRIPTIONS = {
    "historical_reply_rate": "Recipient's past propensity to answer questions or remarks from this sender.",
    "is_question": "Questions naturally prompt a conversational turn and require follow-up.",
    "consecutive_unanswered_sender": "Sending multiple unanswered messages in a row can indicate urgency or follow-up fatigue.",
    "is_recipient_active_hour": "Messages sent when the recipient is historically active on chat are significantly more likely to receive prompt responses.",
    "minutes_since_last_incoming": "Recent conversational momentum makes immediate replies more probable.",
    "has_request_cue": "Clear calls to action or requests prompt faster acknowledgment.",
    "avg_response_time_minutes": "Baseline responsiveness of the recipient in this conversation.",
    "message_length": "Brief or overly verbose messages correlate with different response dynamics.",
    "is_weekend": "Conversational cadence and availability frequently change across weekdays and weekends."
}
