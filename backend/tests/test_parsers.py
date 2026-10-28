import pytest
from datetime import datetime
from backend.app.parsers.whatsapp import WhatsAppParser
from backend.app.parsers.csv_parser import CSVParser
from backend.app.parsers.json_parser import JSONParser
from backend.app.parsers.detector import parse_chat_file


def test_whatsapp_parser_android():
    sample = (
        "15/01/2024, 14:32 - Alex: Hey, are you free for a call?\n"
        "15/01/2024, 14:35 - Jordan: Yes, hopping on in 5 minutes.\n"
        "15/01/2024, 14:36 - Jordan: Sending you the link now.\n"
    )
    parser = WhatsAppParser()
    assert parser.can_parse(sample) is True
    conv = parser.parse(sample, "android_test.txt")

    assert conv.total_messages == 3
    assert len(conv.participants) == 2
    assert "Alex" in conv.participants
    assert "Jordan" in conv.participants
    assert conv.messages[0].sender == "Alex"
    assert conv.messages[0].text == "Hey, are you free for a call?"
    assert conv.messages[0].timestamp.year == 2024
    assert conv.messages[0].timestamp.month == 1
    assert conv.messages[0].timestamp.day == 15


def test_whatsapp_parser_multiline_and_media():
    sample = (
        "[12/05/2023, 10:15:30] Maya: First line of the message\n"
        "Second line continuing here\n"
        "Third line finishing.\n"
        "[12/05/2023, 10:16:00] Liam: <Media omitted>\n"
        "[12/05/2023, 10:17:00] Messages and calls are end-to-end encrypted.\n"
    )
    parser = WhatsAppParser()
    assert parser.can_parse(sample) is True
    conv = parser.parse(sample, "ios_test.txt")

    assert conv.total_messages == 3
    # Multiline check
    assert "Second line continuing here" in conv.messages[0].text
    # Media check
    assert conv.messages[1].is_media is True
    # System check
    assert conv.messages[2].is_system is True
    assert conv.valid_message_count == 2


def test_csv_parser():
    sample = (
        "timestamp,sender,text\n"
        "2024-02-10T14:00:00,UserA,What time is the demo?\n"
        "2024-02-10T14:15:00,UserB,At 3:30 PM in Room B.\n"
    )
    parser = CSVParser()
    assert parser.can_parse(sample) is True
    conv = parser.parse(sample, "test.csv")

    assert conv.total_messages == 2
    assert conv.participants == ["UserA", "UserB"]
    assert conv.messages[0].text == "What time is the demo?"


def test_json_parser():
    sample = (
        '[\n'
        '  {"timestamp": "2024-01-01T12:00:00", "sender": "Sam", "text": "Happy New Year!"},\n'
        '  {"timestamp": "2024-01-01T12:05:00", "sender": "Taylor", "text": "Happy New Year to you too!"}\n'
        ']'
    )
    parser = JSONParser()
    assert parser.can_parse(sample) is True
    conv = parser.parse(sample, "chat.json")

    assert conv.total_messages == 2
    assert conv.participants == ["Sam", "Taylor"]


def test_detector_fallback():
    raw_bytes = b"Just random unstructured notes\nwithout any dates or chat format\nsomewhere."
    conv = parse_chat_file(raw_bytes, "notes.txt")
    assert conv.total_messages == 0
    assert len(conv.warnings) > 0
