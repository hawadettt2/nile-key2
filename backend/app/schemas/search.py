from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    query: str
    entity_type: Optional[str] = None


class SearchResult(BaseModel):
    entity_type: str
    id: int
    title: str
    subtitle: Optional[str] = None
    url: Optional[str] = None
    relevance: Optional[float] = None

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    total: int

    class Config:
        from_attributes = True
