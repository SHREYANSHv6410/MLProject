from typing import List, Dict, Tuple, Optional
from backend.app.schemas.chat import (
    ChatMessage,
    ChatConversation,
    ChatPreviewResponse
)
from backend.app.parsers.detector import parse_chat_file


class ChatService:
    """Handles chat file ingestion, preview computation, and participant candidate selection."""

    @staticmethod
    def process_chat_upload(file_bytes: bytes, filename: str) -> ChatPreviewResponse:
        conversation: ChatConversation = parse_chat_file(file_bytes, filename)

        # Participant counts
        participant_counts: Dict[str, int] = {}
        for m in conversation.messages:
            if not m.is_system and m.sender != "System":
                participant_counts[m.sender] = participant_counts.get(m.sender, 0) + 1

        participants = sorted(list(participant_counts.keys()))

        # Determine sensible defaults
        default_sender: Optional[str] = None
        default_recipient: Optional[str] = None
        default_target_id: Optional[str] = None

        valid_msgs = [m for m in conversation.messages if not m.is_system]

        if len(participants) == 2:
            # If 2 participants, check who sent the last message
            if valid_msgs:
                last_sender = valid_msgs[-1].sender
                default_sender = last_sender
                default_recipient = participants[0] if participants[1] == last_sender else participants[1]
                default_target_id = valid_msgs[-1].id
        elif len(participants) > 2:
            # Choose top 2 participants by message count
            top_two = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)[:2]
            default_sender = top_two[0][0]
            default_recipient = top_two[1][0]
            if valid_msgs:
                # Find latest message from default_sender
                for m in reversed(valid_msgs):
                    if m.sender == default_sender:
                        default_target_id = m.id
                        break

        # Candidate target messages: the last 15 valid messages sent by anyone
        candidate_targets = [m for m in valid_msgs[-20:]]

        # Preview messages (first 20 and last 30 messages)
        if len(conversation.messages) <= 60:
            preview_msgs = conversation.messages
        else:
            preview_msgs = conversation.messages[:20] + conversation.messages[-40:]

        return ChatPreviewResponse(
            filename=filename,
            detected_format=conversation.detected_format,
            participants=participants,
            participant_counts=participant_counts,
            total_messages=conversation.total_messages,
            date_start=conversation.date_start,
            date_end=conversation.date_end,
            warnings=conversation.warnings,
            preview_messages=preview_msgs,
            candidate_target_messages=candidate_targets,
            default_sender=default_sender,
            default_recipient=default_recipient,
            default_target_message_id=default_target_id
        )
