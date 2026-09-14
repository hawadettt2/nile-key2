from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ResearchQuery(BaseModel):
    """A specialized research query for a specific knowledge dimension."""
    query_id: str = Field(description="Unique identifier for this query")
    dimension: str = Field(description="Knowledge dimension this query addresses")
    purpose: str = Field(description="What this query aims to find out")
    query: str = Field(description="The actual query text")
    source_preferences: Optional[List[str]] = Field(default=None, description="Preferred source types or IDs")
    context: Dict[str, Any] = Field(default_factory=dict, description="Query-specific context")
    scope: Optional[Dict[str, Any]] = Field(default=None, description="Query-specific scope constraints")


class ResearchQueryPlan(BaseModel):
    """Plan containing decomposed research queries for an intent."""
    intent_profile: Dict[str, Any] = Field(description="Extracted facts about the intent")
    queries: List[ResearchQuery] = Field(description="Specialized research queries")
    decomposition_strategy: str = Field(default="deterministic_rules", description="Strategy used for decomposition")
