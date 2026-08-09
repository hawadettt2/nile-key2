from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from app.schemas.research import Evidence, Source
from app.research.retrieval.contracts import RetrievedContent


class ProvenanceRecord:
    """Provenance information linking evidence to its origin."""

    def __init__(
        self,
        request_id: str,
        source_id: str,
        source_reference: Optional[str] = None,
        retrieval_timestamp: Optional[datetime] = None,
        content_hash: Optional[str] = None,
        transformation: Optional[str] = None,
    ):
        self.request_id = request_id
        self.source_id = source_id
        self.source_reference = source_reference
        self.retrieval_timestamp = retrieval_timestamp or datetime.utcnow()
        self.content_hash = content_hash
        self.transformation = transformation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_id": self.source_id,
            "source_reference": self.source_reference,
            "retrieval_timestamp": self.retrieval_timestamp.isoformat(),
            "content_hash": self.content_hash,
            "transformation": self.transformation,
        }


class EvidenceCapture(ABC):
    """Abstract interface for capturing evidence from retrieved content."""

    @abstractmethod
    async def capture(
        self,
        content: RetrievedContent,
        source: Optional[Source],
        request_id: str,
        transformation: Optional[str] = None,
    ) -> Evidence:
        ...


class DefaultEvidenceCapture(EvidenceCapture):
    """Default evidence capture implementation."""

    async def capture(
        self,
        content: RetrievedContent,
        source: Optional[Source],
        request_id: str,
        transformation: Optional[str] = None,
    ) -> Evidence:
        content_excerpt = self._extract_excerpt(content)
        source_id = content.source_id or (source.source_id if source else "")
        source_reference = source.reference if source else None
        source_type = source.source_type if source else None
        provenance = ProvenanceRecord(
            request_id=request_id,
            source_id=source_id,
            source_reference=source_reference,
            retrieval_timestamp=datetime.utcnow(),
            transformation=transformation,
        )
        metadata = {}
        if source_type:
            metadata["source_type"] = source_type
        return Evidence(
            evidence_id=f"ev_{request_id}_{source_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            source_id=source_id,
            source_reference=source_reference,
            captured_at=datetime.utcnow(),
            content=content_excerpt,
            evidence_type="processed" if transformation else "raw",
            provenance=provenance.to_dict(),
            metadata=metadata or None,
        )

    def _extract_excerpt(self, content: RetrievedContent) -> str:
        raw = content.raw_content
        if isinstance(raw, str):
            return raw[:500]
        if isinstance(raw, dict):
            return str(raw.get("content", str(raw)))[:500]
        return str(raw)[:500]
