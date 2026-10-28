from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HourlyActivity(BaseModel):
    hour: int
    sender_count: int
    recipient_count: int
    total_count: int


class DayOfWeekActivity(BaseModel):
    day: str
    day_index: int
    count: int


class ResponseTimeBucket(BaseModel):
    bucket: str
    count: int
    percentage: float


class ConversationStats(BaseModel):
    total_messages: int
    sender_messages: int
    recipient_messages: int
    sender_ratio: float
    recipient_ratio: float
    historical_reply_rate: Optional[float] = None
    avg_response_time_minutes: Optional[float] = None
    median_response_time_minutes: Optional[float] = None
    min_response_time_minutes: Optional[float] = None
    max_response_time_minutes: Optional[float] = None
    conversation_duration_days: float
    avg_sender_words: float
    avg_recipient_words: float
    sender_question_count: int
    recipient_question_count: int
    sender_emoji_count: int
    recipient_emoji_count: int
    activity_by_hour: List[HourlyActivity]
    activity_by_day: List[DayOfWeekActivity]
    response_time_distribution: List[ResponseTimeBucket]
    turn_taking_ratio: float
    initiated_conversations_sender: int
    initiated_conversations_recipient: int
