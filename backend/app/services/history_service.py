from typing import List, Dict, Any
from backend.app.schemas.history import HistoryRecord, HistoryListResponse
from backend.app.core.database import get_history, clear_history
from backend.app.core.config import settings


class HistoryService:
    @staticmethod
    def list_history(limit: int = 50) -> HistoryListResponse:
        records_raw = get_history(limit=limit)
        items = [HistoryRecord(**r) for r in records_raw]
        return HistoryListResponse(
            enabled=settings.ENABLE_HISTORY,
            total_count=len(items),
            items=items
        )

    @staticmethod
    def purge_history() -> bool:
        return clear_history()
