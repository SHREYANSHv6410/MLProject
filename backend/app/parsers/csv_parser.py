import csv
import io
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from dateutil import parser as date_parser

from backend.app.parsers.base import BaseParser
from backend.app.schemas.chat import ChatConversation, ChatMessage


class CSVParser(BaseParser):
    """Parser for tabular CSV conversation exports."""

    TIMESTAMP_COLS = ["timestamp", "datetime", "date_time", "time", "date", "created_at", "sent_at"]
    SENDER_COLS = ["sender", "author", "user", "from", "speaker", "participant", "sender_name"]
    TEXT_COLS = ["text", "message", "content", "body", "msg", "message_text"]

    def can_parse(self, content: str) -> bool:
        sample = content.strip().splitlines()[:5]
        if not sample:
            return False
        first_line = sample[0].lower()
        has_time = any(col in first_line for col in self.TIMESTAMP_COLS)
        has_sender = any(col in first_line for col in self.SENDER_COLS)
        has_text = any(col in first_line for col in self.TEXT_COLS)
        return has_time and (has_sender or has_text)

    def _find_column(self, headers: List[str], candidates: List[str]) -> Optional[str]:
        headers_lower = {h.lower().strip().replace('"', '').replace("'", ""): h for h in headers}
        for cand in candidates:
            if cand in headers_lower:
                return headers_lower[cand]
        # Partial match
        for h_clean, orig in headers_lower.items():
            if any(cand in h_clean for cand in candidates):
                return orig
        return None

    def parse(self, content: str, filename: str = "chat.csv") -> ChatConversation:
        warnings: List[str] = []
        messages: List[ChatMessage] = []

        # Sniff delimiter
        delimiter = ","
        try:
            sniffer = csv.Sniffer()
            sample = "\n".join(content.splitlines()[:10])
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            if "\t" in content.splitlines()[0]:
                delimiter = "\t"
            elif ";" in content.splitlines()[0]:
                delimiter = ";"

        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        headers = reader.fieldnames or []

        time_col = self._find_column(headers, self.TIMESTAMP_COLS)
        sender_col = self._find_column(headers, self.SENDER_COLS)
        text_col = self._find_column(headers, self.TEXT_COLS)

        if not time_col or not text_col:
            warnings.append(f"CSV missing mandatory columns. Found headers: {headers}")
            return ChatConversation(
                filename=filename,
                detected_format="CSV (invalid headers)",
                participants=[],
                messages=[],
                warnings=warnings
            )

        for row_idx, row in enumerate(reader, start=2):
            raw_time = row.get(time_col, "").strip()
            raw_sender = row.get(sender_col, "Unknown").strip() if sender_col else "Unknown"
            raw_text = row.get(text_col, "").strip()

            if not raw_time or not raw_text:
                continue

            try:
                dt = date_parser.parse(raw_time)
            except Exception:
                warnings.append(f"Row {row_idx}: Could not parse timestamp '{raw_time}'")
                continue

            messages.append(ChatMessage(
                id=f"msg_{len(messages) + 1}_{uuid.uuid4().hex[:6]}",
                timestamp=dt,
                sender=raw_sender,
                text=raw_text,
                is_media=False,
                is_system=False,
                raw=str(row)
            ))

        messages.sort(key=lambda m: m.timestamp)
        participants = sorted(list({m.sender for m in messages if m.sender != "System"}))
        valid_msgs = [m for m in messages if not m.is_system]

        return ChatConversation(
            filename=filename,
            detected_format=f"CSV (delim: '{delimiter}')",
            participants=participants,
            messages=messages,
            date_start=valid_msgs[0].timestamp if valid_msgs else None,
            date_end=valid_msgs[-1].timestamp if valid_msgs else None,
            warnings=warnings,
            total_messages=len(messages),
            valid_message_count=len(valid_msgs)
        )
