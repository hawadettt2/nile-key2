import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider

logger = logging.getLogger(__name__)


class RegulationsKnowledgeProvider(KnowledgeProvider):
    """Knowledge Provider implementation for local regulation files.

    Reads a local JSON file containing regulation records, transforms them
    into the KnowledgeProvider query return shape, and exposes them via
    the Company Knowledge Layer.
    """

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._records: List[Dict[str, Any]] = []
        self._load_file()

    def _load_file(self) -> None:
        if not os.path.exists(self._file_path):
            logger.warning("Regulations file not found: %s", self._file_path)
            self._records = []
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.warning(
                    "Regulations file must contain a JSON array: %s", self._file_path
                )
                self._records = []
                return

            self._records = [
                record for record in data if isinstance(record, dict)
            ]
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load regulations file %s: %s", self._file_path, exc)
            self._records = []

    def _confidence_for(self, record: Dict[str, Any]) -> float:
        effective_date = record.get("effective_date")
        if effective_date is None or str(effective_date).strip() == "":
            return 0.5

        source_url = record.get("source_url")
        if source_url and str(source_url).strip():
            return 0.85

        return 0.75

    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        records = self._records
        if scope:
            records = [
                record
                for record in records
                if record.get("regulation_type") == scope
                or record.get("category") == scope
                or record.get("country") == scope
            ]

        if query:
            lowered = query.lower()
            records = [
                record
                for record in records
                if lowered in str(record.get("title", "")).lower()
                or lowered in str(record.get("description", "")).lower()
                or lowered in str(record.get("regulation_type", "")).lower()
                or lowered in str(record.get("category", "")).lower()
            ]

        results = []
        for record in records[:limit]:
            results.append({
                "id": str(record.get("id", "")),
                "content": (
                    str(record.get("title", "")) + " - " + str(record.get("description", ""))
                ).strip(),
                "source_id": "regulations",
                "confidence": self._confidence_for(record),
                "metadata": {
                    "regulation_type": record.get("regulation_type"),
                    "category": record.get("category"),
                    "country": record.get("country"),
                    "effective_date": record.get("effective_date"),
                    "source_url": record.get("source_url"),
                    "version": record.get("version"),
                },
            })

        confidence = 0.0 if not results else sum(item["confidence"] for item in results) / len(results)
        return {
            "results": results,
            "confidence": confidence,
            "sources": ["regulations"],
        }

    async def get_sources(self) -> List[Dict[str, Any]]:
        try:
            mtime = os.path.getmtime(self._file_path)
            updated_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        except OSError:
            updated_at = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

        return [
            {
                "id": "regulations",
                "name": "Regulations Knowledge",
                "type": "regulation",
                "version": "1.0.0",
                "updated_at": updated_at,
            }
        ]
