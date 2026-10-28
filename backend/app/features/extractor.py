import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from backend.app.schemas.chat import ChatMessage
from backend.app.features.schema import FEATURE_COLUMNS


REQUEST_PATTERNS = re.compile(
    r"\b(can you|could you|would you|please|let me know|ping me|tell me|call me|what do you think|"
    r"are you free|are you available|let's meet|check this|update me|let me understand|send me)\b",
    re.IGNORECASE
)

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

# Basic regex for emoji matching
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE
)


class FeatureExtractor:
    """
    Extracts strictly leak-free feature vectors for reply prediction.
    Only messages preceding the target message timestamp are used for historical calculation.
    """

    def __init__(self, reply_horizon_hours: float = 24.0):
        self.reply_horizon_hours = reply_horizon_hours

    def extract_features_for_message(
        self,
        messages: List[ChatMessage],
        target_idx: int,
        sender: str,
        recipient: str
    ) -> Dict[str, Any]:
        """
        Extract features for messages[target_idx].
        Assumes messages are strictly sorted by timestamp ascending.
        """
        target_msg = messages[target_idx]
        target_time = target_msg.timestamp
        target_text = target_msg.text or ""

        # --- A. Message-level Features ---
        msg_len = len(target_text)
        words = target_text.split()
        word_count = len(words)
        q_count = target_text.count("?")
        has_question_word = bool(re.search(r"\b(what|why|how|when|where|who|which|whose|whom|is|are|do|does|can|could|will|would)\b", target_text, re.I))
        is_question = 1 if (q_count > 0 or (has_question_word and target_text.strip().endswith("?"))) else 0
        has_req = 1 if bool(REQUEST_PATTERNS.search(target_text)) else 0
        emoji_count = len(EMOJI_PATTERN.findall(target_text))
        excl_count = target_text.count("!")
        upper_letters = sum(1 for c in target_text if c.isupper())
        total_letters = sum(1 for c in target_text if c.isalpha())
        upper_ratio = (upper_letters / max(1, total_letters)) if total_letters > 0 else 0.0
        has_url = 1 if bool(URL_PATTERN.search(target_text)) else 0
        is_media = 1 if target_msg.is_media else 0

        # --- B. Past Messages Only (Strict Leakage Prevention) ---
        past_msgs = [m for i, m in enumerate(messages) if i < target_idx and not m.is_system]

        prior_sender_msgs = [m for m in past_msgs if m.sender == sender]
        prior_recipient_msgs = [m for m in past_msgs if m.sender == recipient]

        prev_count = len(past_msgs)
        sender_count = len(prior_sender_msgs)
        recipient_count = len(prior_recipient_msgs)
        sender_recip_ratio = (sender_count + 1.0) / (recipient_count + 1.0)

        # Minutes since last incoming message from recipient
        if prior_recipient_msgs:
            last_incoming_time = prior_recipient_msgs[-1].timestamp
            mins_since_last_incoming = max(0.0, (target_time - last_incoming_time).total_seconds() / 60.0)
        else:
            mins_since_last_incoming = 1440.0  # default 24h if no prior recipient message

        # Consecutive unanswered sender messages immediately before target
        consec_sender = 0
        for m in reversed(past_msgs):
            if m.sender == sender:
                consec_sender += 1
            else:
                break

        # Historical response times and reply rate from past turns
        reply_times_minutes: List[float] = []
        replied_turns = 0
        total_eval_turns = 0

        # Group past messages into conversational turns
        turns: List[Tuple[str, datetime, datetime]] = []
        for m in past_msgs:
            if not turns or turns[-1][0] != m.sender:
                turns.append((m.sender, m.timestamp, m.timestamp))
            else:
                s, s_time, _ = turns[-1]
                turns[-1] = (s, s_time, m.timestamp)

        for i, turn in enumerate(turns):
            turn_sender, turn_start, turn_end = turn
            if turn_sender == sender:
                total_eval_turns += 1
                # Did recipient take the next turn?
                if i + 1 < len(turns) and turns[i + 1][0] == recipient:
                    next_resp_time = turns[i + 1][1]
                    delta_mins = (next_resp_time - turn_end).total_seconds() / 60.0
                    if delta_mins >= 0 and delta_mins <= (self.reply_horizon_hours * 60):
                        replied_turns += 1
                        reply_times_minutes.append(delta_mins)

        if total_eval_turns > 0:
            hist_reply_rate = replied_turns / total_eval_turns
        else:
            hist_reply_rate = 0.50  # Uninformative prior when cold-start

        if reply_times_minutes:
            avg_resp_time = float(np.mean(reply_times_minutes))
            med_resp_time = float(np.median(reply_times_minutes))
        else:
            avg_resp_time = 120.0  # 2 hours baseline
            med_resp_time = 60.0

        # Recipient active hours calculation from prior recipient messages
        recipient_active_hours = set()
        if len(prior_recipient_msgs) >= 5:
            recip_hours = [m.timestamp.hour for m in prior_recipient_msgs]
            hour_counts = pd.Series(recip_hours).value_counts()
            active_threshold = max(1, int(len(prior_recipient_msgs) * 0.08))
            recipient_active_hours = set(hour_counts[hour_counts >= active_threshold].index)
        else:
            # Daytime 08:00 - 22:00 default
            recipient_active_hours = set(range(8, 23))

        target_hour = target_time.hour
        is_recip_active_hour = 1 if target_hour in recipient_active_hours else 0

        # --- C. Temporal Features ---
        day_of_week = target_time.weekday()  # 0=Monday, 6=Sunday
        is_weekend = 1 if day_of_week in (5, 6) else 0

        features = {
            "message_length": int(msg_len),
            "word_count": int(word_count),
            "question_mark_count": int(q_count),
            "is_question": int(is_question),
            "has_request_cue": int(has_req),
            "emoji_count": int(emoji_count),
            "exclamation_count": int(excl_count),
            "uppercase_ratio": float(round(upper_ratio, 4)),
            "has_url": int(has_url),
            "is_media": int(is_media),
            "historical_reply_rate": float(round(hist_reply_rate, 4)),
            "previous_messages_count": int(prev_count),
            "sender_message_count": int(sender_count),
            "recipient_message_count": int(recipient_count),
            "sender_recipient_ratio": float(round(sender_recip_ratio, 4)),
            "consecutive_unanswered_sender": int(consec_sender),
            "avg_response_time_minutes": float(round(avg_resp_time, 2)),
            "median_response_time_minutes": float(round(med_resp_time, 2)),
            "minutes_since_last_incoming": float(round(mins_since_last_incoming, 2)),
            "hour_of_day": int(target_hour),
            "day_of_week": int(day_of_week),
            "is_weekend": int(is_weekend),
            "is_recipient_active_hour": int(is_recip_active_hour)
        }

        return features

    def extract_features_df(
        self,
        messages: List[ChatMessage],
        target_indices: List[int],
        sender: str,
        recipient: str
    ) -> pd.DataFrame:
        """Extract features for multiple message indices as a pandas DataFrame."""
        rows = []
        for idx in target_indices:
            row = self.extract_features_for_message(messages, idx, sender, recipient)
            rows.append(row)
        return pd.DataFrame(rows, columns=FEATURE_COLUMNS)
