from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    timestamp: datetime = Field(..., description="Parsed timestamp of the message")
    sender: str = Field(..., description="Sender display name or phone number")
    text: str = Field(..., description="Message body text")
    is_media: bool = Field(default=False, description="Whether message is a media placeholder")
    is_system: bool = Field(default=False, description="Whether message is a system notification")
    raw: Optional[str] = Field(default=None, description="Original raw line before parsing")


class ChatConversation(BaseModel):
    filename: str
    detected_format: str
    participants: List[str]
    messages: List[ChatMessage]
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    warnings: List[str] = Field(default_factory=list)
    total_messages: int = 0
    valid_message_count: int = 0


class ChatPreviewResponse(BaseModel):
    filename: str
    detected_format: str
    participants: List[str]
    participant_counts: Dict[str, int]
    total_messages: int
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    warnings: List[str]
    preview_messages: List[ChatMessage]
    candidate_target_messages: List[ChatMessage]
    default_sender: Optional[str] = None
    default_recipient: Optional[str] = None
    default_target_message_id: Optional[str] = None


class PredictRequest(BaseModel):
    messages: List[ChatMessage]
    sender: str
    recipient: str
    target_message_id: Optional[str] = None
    reply_horizon_hours: float = Field(default=24.0, ge=1.0, le=168.0)
