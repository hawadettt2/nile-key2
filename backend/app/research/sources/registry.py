from typing import Dict, List, Optional

from app.schemas.research import Source, SourceRegistration


class SourceRegistry:
    """Registry for external research sources."""

    def __init__(self):
        self._sources: Dict[str, Source] = {}

    def register(self, registration: SourceRegistration) -> Source:
        source = registration.source
        if not source.source_id:
            raise ValueError("source_id is required")
        existing = self._sources.get(source.source_id)
        if existing and not registration.overwrite:
            raise ValueError(
                f"Source '{source.source_id}' already exists. Set overwrite=True to replace."
            )
        self._sources[source.source_id] = source
        return source

    def get(self, source_id: str) -> Optional[Source]:
        return self._sources.get(source_id)

    def list(self) -> List[Source]:
        return list(self._sources.values())

    def unregister(self, source_id: str) -> bool:
        if source_id in self._sources:
            del self._sources[source_id]
            return True
        return False

    def clear(self) -> None:
        self._sources.clear()
