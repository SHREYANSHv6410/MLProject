from abc import ABC, abstractmethod
from typing import Tuple
from backend.app.schemas.chat import ChatConversation


class BaseParser(ABC):
    """Abstract base class for all conversation parsers."""

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Return True if content matches this parser's target format."""
        pass

    @abstractmethod
    def parse(self, content: str, filename: str = "chat") -> ChatConversation:
        """Parse raw content into structured ChatConversation."""
        pass
