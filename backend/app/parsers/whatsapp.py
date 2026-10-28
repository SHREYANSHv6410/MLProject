import re
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from dateutil import parser as date_parser

from backend.app.parsers.base import BaseParser
from backend.app.schemas.chat import ChatConversation, ChatMessage


class WhatsAppParser(BaseParser):
    """Robust parser for WhatsApp text chat exports (iOS and Android formats)."""

    # Android: "12/05/2023, 14:23 - Sender: Message" or "12/5/23, 2:23 PM - Sender: Message"
    ANDROID_PATTERN = re.compile(
        r"^(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\s+-\s+([^:]+):\s*(.*)$",
        re.UNICODE
    )

    # iOS: "[12/05/2023, 14:23:45] Sender: Message" or "[12/5/23, 2:23:45 PM] Sender: Message"
    IOS_PATTERN = re.compile(
        r"^\[(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\]\s+([^:]+):\s*(.*)$",
        re.UNICODE
    )

    # System line without sender colon: "12/05/2023, 14:23 - Messages and calls are end-to-end encrypted..."
    ANDROID_SYSTEM_PATTERN = re.compile(
        r"^(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\s+-\s+(.+)$",
        re.UNICODE
    )
    IOS_SYSTEM_PATTERN = re.compile(
        r"^\[(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\]\s+(.+)$",
        re.UNICODE
    )

    MEDIA_MARKERS = [
        "<media omitted>",
        "image omitted",
        "video omitted",
        "audio omitted",
        "sticker omitted",
        "document omitted",
        "contact card omitted",
        "voice message omitted",
        "gif omitted",
        "photo omitted"
    ]

    SYSTEM_KEYWORDS = [
        "end-to-end encrypted",
        "created group",
        "changed the group",
        "added you",
        "added",
        "left",
        "removed",
        "security code changed",
        "changed this group's icon",
        "changed their phone number"
    ]

    def can_parse(self, content: str) -> bool:
        sample_lines = [line.strip() for line in content.splitlines()[:50] if line.strip()]
        matches = 0
        for line in sample_lines:
            if self.ANDROID_PATTERN.match(line) or self.IOS_PATTERN.match(line):
                matches += 1
        return matches >= max(1, min(len(sample_lines) // 4, 3))

    def _parse_timestamp(self, date_str: str, time_str: str) -> Optional[datetime]:
        clean_date = date_str.strip().replace(".", "/").replace("-", "/")
        clean_time = time_str.strip().replace("\u202f", " ")  # narrow no-break space in modern WhatsApp
        datetime_str = f"{clean_date} {clean_time}"
        
        try:
            # First try standard dayfirst formats common in WhatsApp
            return date_parser.parse(datetime_str, dayfirst=True)
        except Exception:
            try:
                return date_parser.parse(datetime_str, dayfirst=False)
            except Exception:
                return None

    def parse(self, content: str, filename: str = "chat.txt") -> ChatConversation:
        raw_lines = content.splitlines()
        messages: List[ChatMessage] = []
        warnings: List[str] = []
        current_msg: Optional[ChatMessage] = None

        for idx, line in enumerate(raw_lines):
            line_str = line.strip("\ufeff\u200e\u200f\r")  # Remove UTF BOM and LTR/RTL marks
            if not line_str.strip():
                if current_msg:
                    current_msg.text += "\n"
                continue

            android_match = self.ANDROID_PATTERN.match(line_str)
            ios_match = self.IOS_PATTERN.match(line_str)

            if android_match or ios_match:
                # Save previous message
                if current_msg:
                    messages.append(current_msg)

                match = android_match or ios_match
                d_str, t_str, sender, text = match.group(1), match.group(2), match.group(3).strip(), match.group(4).strip()
                parsed_dt = self._parse_timestamp(d_str, t_str)

                if not parsed_dt:
                    warnings.append(f"Line {idx + 1}: Could not parse timestamp '{d_str} {t_str}'. Skipped.")
                    current_msg = None
                    continue

                lower_text = text.lower()
                is_media = any(marker in lower_text for marker in self.MEDIA_MARKERS)
                is_system = any(sys_kw in lower_text for sys_kw in self.SYSTEM_KEYWORDS)

                current_msg = ChatMessage(
                    id=f"msg_{len(messages) + 1}_{uuid.uuid4().hex[:6]}",
                    timestamp=parsed_dt,
                    sender=sender,
                    text=text,
                    is_media=is_media,
                    is_system=is_system,
                    raw=line_str
                )
            else:
                # Check if it's a system line without sender
                sys_android = self.ANDROID_SYSTEM_PATTERN.match(line_str)
                sys_ios = self.IOS_SYSTEM_PATTERN.match(line_str)
                if sys_android or sys_ios:
                    if current_msg:
                        messages.append(current_msg)
                    match = sys_android or sys_ios
                    d_str, t_str, text = match.group(1), match.group(2), match.group(3).strip()
                    parsed_dt = self._parse_timestamp(d_str, t_str)
                    if parsed_dt:
                        current_msg = ChatMessage(
                            id=f"msg_{len(messages) + 1}_{uuid.uuid4().hex[:6]}",
                            timestamp=parsed_dt,
                            sender="System",
                            text=text,
                            is_media=False,
                            is_system=True,
                            raw=line_str
                        )
                        continue

                # Continuation line for multiline message
                if current_msg:
                    current_msg.text += "\n" + line_str
                else:
                    if idx < 5:
                        warnings.append(f"Line {idx + 1}: Unrecognized header format '{line_str[:50]}...'")

        if current_msg:
            messages.append(current_msg)

        # Sort chronologically
        messages.sort(key=lambda m: m.timestamp)

        # Participant identification (exclude System)
        participants = sorted(list({m.sender for m in messages if not m.is_system and m.sender != "System"}))
        valid_msgs = [m for m in messages if not m.is_system]

        date_start = valid_msgs[0].timestamp if valid_msgs else None
        date_end = valid_msgs[-1].timestamp if valid_msgs else None

        if len(participants) < 2:
            warnings.append(f"Detected only {len(participants)} participant(s). Two participants are recommended for reply analysis.")

        return ChatConversation(
            filename=filename,
            detected_format="WhatsApp (txt)",
            participants=participants,
            messages=messages,
            date_start=date_start,
            date_end=date_end,
            warnings=warnings,
            total_messages=len(messages),
            valid_message_count=len(valid_msgs)
        )
