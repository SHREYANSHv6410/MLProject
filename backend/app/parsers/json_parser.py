import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dateutil import parser as date_parser

from backend.app.parsers.base import BaseParser
from backend.app.schemas.chat import ChatConversation, ChatMessage


class JSONParser(BaseParser):
    """Parser for structured JSON conversations (direct array, Telegram export, Discord)."""

    def can_parse(self, content: str) -> bool:
        trimmed = content.strip()
        return (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]"))

    def _extract_text(self, text_field: Any) -> str:
        if isinstance(text_field, str):
            return text_field
        if isinstance(text_field, list):
            # Telegram sometimes outputs rich entities as list of dicts/strings
            parts = []
            for item in text_field:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
            return "".join(parts)
        return str(text_field)

    def parse(self, content: str, filename: str = "chat.json") -> ChatConversation:
        warnings: List[str] = []
        messages: List[ChatMessage] = []

        try:
            data = json.loads(content)
        except Exception as e:
            return ChatConversation(
                filename=filename,
                detected_format="Invalid JSON",
                participants=[],
                messages=[],
                warnings=[f"Failed to parse JSON file: {str(e)}"]
            )

        raw_messages: List[Dict[str, Any]] = []
        if isinstance(data, list):
            raw_messages = data
        elif isinstance(data, dict):
            if "messages" in data and isinstance(data["messages"], list):
                raw_messages = data["messages"]
            elif "chats" in data and isinstance(data["chats"], list):
                raw_messages = data["chats"]
            else:
                warnings.append("Could not find message list in JSON object root.")

        for idx, item in enumerate(raw_messages):
            if not isinstance(item, dict):
                continue

            # Telegram / Discord / Generic mapping
            time_val = (
                item.get("timestamp") or 
                item.get("date") or 
                item.get("datetime") or 
                item.get("time") or
                item.get("created_at")
            )
            sender_val = (
                item.get("sender") or 
                item.get("from") or 
                item.get("author") or 
                item.get("user") or 
                item.get("speaker") or
                "Unknown"
            )
            text_val = (
                item.get("text") or 
                item.get("message") or 
                item.get("content") or 
                item.get("body") or 
                ""
            )

            if not time_val:
                continue

            try:
                if isinstance(time_val, (int, float)):
                    # Unix timestamp
                    dt = datetime.fromtimestamp(time_val)
                else:
                    dt = date_parser.parse(str(time_val))
            except Exception:
                warnings.append(f"Item {idx}: Failed to parse timestamp '{time_val}'")
                continue

            clean_text = self._extract_text(text_val)
            is_media = bool(item.get("media_type") or item.get("photo") or item.get("file"))
            msg_type = item.get("type", "message")
            is_system = msg_type != "message" or sender_val == "System"

            messages.append(ChatMessage(
                id=str(item.get("id", f"msg_{len(messages)+1}_{uuid.uuid4().hex[:6]}")),
                timestamp=dt,
                sender=str(sender_val),
                text=clean_text,
                is_media=is_media,
                is_system=is_system,
                raw=json.dumps(item)[:200]
            ))

        messages.sort(key=lambda m: m.timestamp)
        participants = sorted(list({m.sender for m in messages if not m.is_system and m.sender != "System"}))
        valid_msgs = [m for m in messages if not m.is_system]

        return ChatConversation(
            filename=filename,
            detected_format="JSON (structured)",
            participants=participants,
            messages=messages,
            date_start=valid_msgs[0].timestamp if valid_msgs else None,
            date_end=valid_msgs[-1].timestamp if valid_msgs else None,
            warnings=warnings,
            total_messages=len(messages),
            valid_message_count=len(valid_msgs)
        )
