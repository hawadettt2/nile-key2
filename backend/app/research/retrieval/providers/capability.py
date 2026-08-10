from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ProviderCapability:
    """Provider-agnostic description of a search provider's capabilities.

    Selection rules must be based on these capabilities, not on provider names.
    """

    provider_id: str
    supports_web_search: bool = True
    supports_source_urls: bool = False
    supports_snippets: bool = False
    supports_content_fetch: bool = False
    supports_time_range: bool = False
    supports_domain_filter: bool = False
    requires_api_key: bool = False
    has_usage_limit: bool = False
    usage_limit_description: Optional[str] = None
    priority: int = 100
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)
