import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.app.core.config import settings


def init_db():
    """Initialize SQLite database for prediction history if enabled."""
    if not settings.ENABLE_HISTORY:
        return
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                target_message_text TEXT NOT NULL,
                target_message_time TEXT NOT NULL,
                predicted_outcome TEXT NOT NULL,
                probability REAL NOT NULL,
                uncertainty_level TEXT NOT NULL,
                key_factors_json TEXT NOT NULL,
                reply_horizon_hours REAL NOT NULL
            )
        """)
        conn.commit()


def save_prediction(
    prediction_id: str,
    filename: str,
    sender: str,
    recipient: str,
    target_message_text: str,
    target_message_time: datetime,
    predicted_outcome: str,
    probability: float,
    uncertainty_level: str,
    key_factors: List[str],
    reply_horizon_hours: float
) -> bool:
    if not settings.ENABLE_HISTORY:
        return False
    try:
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prediction_history (
                    id, created_at, filename, sender, recipient,
                    target_message_text, target_message_time,
                    predicted_outcome, probability, uncertainty_level,
                    key_factors_json, reply_horizon_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction_id,
                datetime.utcnow().isoformat(),
                filename,
                sender,
                recipient,
                target_message_text[:300],  # Truncate for privacy
                target_message_time.isoformat(),
                predicted_outcome,
                round(probability, 4),
                uncertainty_level,
                json.dumps(key_factors),
                reply_horizon_hours
            ))
            conn.commit()
            return True
    except Exception:
        return False


def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    if not settings.ENABLE_HISTORY or not settings.DATABASE_PATH.exists():
        return []
    try:
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prediction_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "filename": row["filename"],
                    "sender": row["sender"],
                    "recipient": row["recipient"],
                    "target_message_text": row["target_message_text"],
                    "target_message_time": row["target_message_time"],
                    "predicted_outcome": row["predicted_outcome"],
                    "probability": row["probability"],
                    "uncertainty_level": row["uncertainty_level"],
                    "key_factors_summary": json.loads(row["key_factors_json"]),
                    "reply_horizon_hours": row["reply_horizon_hours"]
                })
            return results
    except Exception:
        return []


def clear_history() -> bool:
    if not settings.DATABASE_PATH.exists():
        return True
    try:
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prediction_history")
            conn.commit()
            return True
    except Exception:
        return False
