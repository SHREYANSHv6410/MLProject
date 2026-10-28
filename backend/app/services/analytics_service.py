from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from backend.app.schemas.chat import ChatMessage
from backend.app.schemas.analysis import (
    ConversationStats,
    HourlyActivity,
    DayOfWeekActivity,
    ResponseTimeBucket
)
from backend.app.features.extractor import EMOJI_PATTERN


class AnalyticsService:
    """Computes comprehensive statistical insights and chart datasets for a conversation."""

    @staticmethod
    def analyze_conversation(
        messages: List[ChatMessage],
        sender: str,
        recipient: str,
        reply_horizon_hours: float = 24.0
    ) -> ConversationStats:
        valid_msgs = [m for m in messages if not m.is_system]
        if not valid_msgs:
            return ConversationStats(
                total_messages=0,
                sender_messages=0,
                recipient_messages=0,
                sender_ratio=0.0,
                recipient_ratio=0.0,
                conversation_duration_days=0.0,
                avg_sender_words=0.0,
                avg_recipient_words=0.0,
                sender_question_count=0,
                recipient_question_count=0,
                sender_emoji_count=0,
                recipient_emoji_count=0,
                activity_by_hour=[],
                activity_by_day=[],
                response_time_distribution=[],
                turn_taking_ratio=0.0,
                initiated_conversations_sender=0,
                initiated_conversations_recipient=0
            )

        valid_msgs.sort(key=lambda m: m.timestamp)
        sender_msgs = [m for m in valid_msgs if m.sender == sender]
        recip_msgs = [m for m in valid_msgs if m.sender == recipient]

        total_cnt = len(valid_msgs)
        s_cnt = len(sender_msgs)
        r_cnt = len(recip_msgs)

        s_ratio = round(s_cnt / max(1, total_cnt), 4)
        r_ratio = round(r_cnt / max(1, total_cnt), 4)

        duration_days = max(
            0.01,
            round((valid_msgs[-1].timestamp - valid_msgs[0].timestamp).total_seconds() / 86400.0, 2)
        )

        # Word counts & questions & emojis
        s_words = [len(m.text.split()) for m in sender_msgs if m.text]
        r_words = [len(m.text.split()) for m in recip_msgs if m.text]
        avg_s_words = round(float(np.mean(s_words)), 1) if s_words else 0.0
        avg_r_words = round(float(np.mean(r_words)), 1) if r_words else 0.0

        s_q = sum(1 for m in sender_msgs if "?" in m.text)
        r_q = sum(1 for m in recip_msgs if "?" in m.text)

        s_emoji = sum(len(EMOJI_PATTERN.findall(m.text)) for m in sender_msgs if m.text)
        r_emoji = sum(len(EMOJI_PATTERN.findall(m.text)) for m in recip_msgs if m.text)

        # Turns and response times
        turns = []
        for m in valid_msgs:
            if not turns or turns[-1]["sender"] != m.sender:
                turns.append({"sender": m.sender, "start": m.timestamp, "end": m.timestamp})
            else:
                turns[-1]["end"] = m.timestamp

        response_times_minutes: List[float] = []
        sender_turns_count = 0
        replied_sender_turns = 0

        for i in range(len(turns) - 1):
            curr_turn = turns[i]
            next_turn = turns[i + 1]

            if curr_turn["sender"] == sender:
                sender_turns_count += 1
                if next_turn["sender"] == recipient:
                    delta_mins = (next_turn["start"] - curr_turn["end"]).total_seconds() / 60.0
                    if 0 <= delta_mins <= (reply_horizon_hours * 60):
                        replied_sender_turns += 1
                        response_times_minutes.append(delta_mins)

        # Handle the very last turn if it was sender's
        if turns and turns[-1]["sender"] == sender:
            sender_turns_count += 1

        hist_reply_rate = (
            round(replied_sender_turns / sender_turns_count, 4)
            if sender_turns_count > 0 else None
        )

        avg_resp = round(float(np.mean(response_times_minutes)), 1) if response_times_minutes else None
        med_resp = round(float(np.median(response_times_minutes)), 1) if response_times_minutes else None
        min_resp = round(float(np.min(response_times_minutes)), 1) if response_times_minutes else None
        max_resp = round(float(np.max(response_times_minutes)), 1) if response_times_minutes else None

        # Response time distribution buckets
        buckets = [
            ("< 5 min", 0, 5),
            ("5-15 min", 5, 15),
            ("15-60 min", 15, 60),
            ("1-4 hrs", 60, 240),
            ("4-24 hrs", 240, 1440),
            ("> 24 hrs", 1440, float("inf")),
        ]
        bucket_counts = {b[0]: 0 for b in buckets}
        for rt in response_times_minutes:
            for label, low, high in buckets:
                if low <= rt < high:
                    bucket_counts[label] += 1
                    break

        total_rt = len(response_times_minutes) or 1
        dist_list = [
            ResponseTimeBucket(
                bucket=label,
                count=cnt,
                percentage=round((cnt / total_rt) * 100.0, 1)
            )
            for label, cnt in bucket_counts.items()
        ]

        # Activity by hour (0 to 23)
        hourly_data: List[HourlyActivity] = []
        for h in range(24):
            s_h = sum(1 for m in sender_msgs if m.timestamp.hour == h)
            r_h = sum(1 for m in recip_msgs if m.timestamp.hour == h)
            hourly_data.append(HourlyActivity(
                hour=h,
                sender_count=s_h,
                recipient_count=r_h,
                total_count=s_h + r_h
            ))

        # Activity by day of week (Monday to Sunday)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_counts = [0] * 7
        for m in valid_msgs:
            day_counts[m.timestamp.weekday()] += 1

        daily_data = [
            DayOfWeekActivity(day=day_names[i], day_index=i, count=day_counts[i])
            for i in range(7)
        ]

        # Initiated conversations (gap > 6 hours signifies a new session)
        init_s = 0
        init_r = 0
        if valid_msgs:
            if valid_msgs[0].sender == sender:
                init_s += 1
            else:
                init_r += 1

        for i in range(1, len(valid_msgs)):
            delta_h = (valid_msgs[i].timestamp - valid_msgs[i - 1].timestamp).total_seconds() / 3600.0
            if delta_h >= 6.0:
                if valid_msgs[i].sender == sender:
                    init_s += 1
                elif valid_msgs[i].sender == recipient:
                    init_r += 1

        turn_taking_ratio = round(len(turns) / max(1, total_cnt), 4)

        return ConversationStats(
            total_messages=total_cnt,
            sender_messages=s_cnt,
            recipient_messages=r_cnt,
            sender_ratio=s_ratio,
            recipient_ratio=r_ratio,
            historical_reply_rate=hist_reply_rate,
            avg_response_time_minutes=avg_resp,
            median_response_time_minutes=med_resp,
            min_response_time_minutes=min_resp,
            max_response_time_minutes=max_resp,
            conversation_duration_days=duration_days,
            avg_sender_words=avg_s_words,
            avg_recipient_words=avg_r_words,
            sender_question_count=s_q,
            recipient_question_count=r_q,
            sender_emoji_count=s_emoji,
            recipient_emoji_count=r_emoji,
            activity_by_hour=hourly_data,
            activity_by_day=daily_data,
            response_time_distribution=dist_list,
            turn_taking_ratio=turn_taking_ratio,
            initiated_conversations_sender=init_s,
            initiated_conversations_recipient=init_r
        )
