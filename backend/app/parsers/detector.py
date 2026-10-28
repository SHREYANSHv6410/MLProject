from typing import Tuple
from backend.app.parsers.whatsapp import WhatsAppParser
from backend.app.parsers.csv_parser import CSVParser
from backend.app.parsers.json_parser import JSONParser
from backend.app.parsers.base import BaseParser
from backend.app.schemas.chat import ChatConversation


def parse_chat_file(content_bytes: bytes, filename: str) -> ChatConversation:
    """Detect file format and parse into a ChatConversation object."""
    # Decode text with fallback
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            content_str = content_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        return ChatConversation(
            filename=filename,
            detected_format="Unsupported Encoding",
            participants=[],
            messages=[],
            warnings=["Unable to decode file text with UTF-8 or standard encodings."]
        )

    ext = filename.lower().split(".")[-1] if "." in filename else ""

    parsers = [
        WhatsAppParser(),
        JSONParser(),
        CSVParser()
    ]

    # Prioritize based on extension
    if ext in ("json",):
        parsers = [JSONParser(), WhatsAppParser(), CSVParser()]
    elif ext in ("csv", "tsv"):
        parsers = [CSVParser(), WhatsAppParser(), JSONParser()]
    elif ext in ("txt",):
        parsers = [WhatsAppParser(), CSVParser(), JSONParser()]

    for parser in parsers:
        if parser.can_parse(content_str):
            conv = parser.parse(content_str, filename=filename)
            if conv.messages:
                return conv

    # Fallback attempt WhatsApp as it is the most common .txt export format
    conv = WhatsAppParser().parse(content_str, filename=filename)
    if conv.messages:
        return conv

    return ChatConversation(
        filename=filename,
        detected_format="Unrecognized Format",
        participants=[],
        messages=[],
        warnings=[
            "Could not reliably detect conversation structure. "
            "Please upload a standard WhatsApp export (.txt), CSV with timestamp/sender/text columns, or JSON chat export."
        ]
    )
