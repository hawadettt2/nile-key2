from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.routers.auth import get_current_user
from app.schemas.search import SearchResponse
from app.services.search import search_all

router = APIRouter(tags=["Search"])


@router.get("/api/v1/search", response_model=SearchResponse)
def search(
    query: str = Query(..., description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    current_user: dict = Depends(get_current_user),
):
    return search_all(query=query, entity_type=entity_type)
