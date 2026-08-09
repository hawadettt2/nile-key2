from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from app.schemas.research import Source


class RetrievalStatus(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CONNECTION_FAILURE = "connection_failure"
    INVALID_RESPONSE = "invalid_response"
    UNSUPPORTED_SOURCE = "unsupported_source"
    PROCESSING_FAILURE = "processing_failure"
    FAILED = "failed"


class RetrievedContent:
    """Content retrieved from a source."""

    def __init__(
        self,
        source_id: str,
        raw_content: Any,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source_id = source_id
        self.raw_content = raw_content
        self.content_type = content_type
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "raw_content": self.raw_content,
            "content_type": self.content_type,
            "metadata": self.metadata,
        }


class RetrievalResult:
    """Result of retrieving content from a single source."""

    def __init__(
        self,
        source_id: str,
        status: RetrievalStatus,
        content: Optional[RetrievedContent] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source_id = source_id
        self.status = status
        self.content = content
        self.error = error
        self.duration_ms = duration_ms
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "status": self.status.value,
            "content": self.content.to_dict() if self.content else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class SourceRetriever(ABC):
    """Base class for source retrievers."""

    @abstractmethod
    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        ...


class ContentProcessor(ABC):
    """Base class for content processors."""

    @abstractmethod
    async def process(self, content: RetrievedContent) -> Optional[RetrievedContent]:
        ...
