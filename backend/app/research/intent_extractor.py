from typing import Any, Dict


def _normalize_arabic(text: str) -> str:
    """Normalize Arabic text for matching."""
    text = text.replace("إ", "ا").replace("أ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي").replace("ة", "ه")
    return text


def extract_intent_facts(intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Extract deterministic facts from a business intent.

    This is the single source of truth for intent parsing.
    Both ReasoningEngine and ResearchQueryPlanner must use this
    to avoid duplicate parsers and conflicting extractions.
    """
    intent_lower = intent.lower()
    normalized_intent = _normalize_arabic(intent_lower)
    extracted: Dict[str, Any] = {}

    country_map = {
        "مصر": "818",
        "Egypt": "818",
        "الأردن": "400",
        "Jordan": "400",
    }

    commodity_map = {
        "خضر": "07",
        "vegetables": "07",
        "خضروات": "07",
        "فواكه": "08",
        "فاكهة": "08",
        "fruits": "08",
    }

    request_type_map = {
        "تصدير": "export",
        "export": "export",
        "استيراد": "import",
        "import": "import",
        "دراسة جدوى": "market_study",
        "دراسة سوق": "market_study",
        "market study": "market_study",
        "market research": "market_research",
        "بحث": "market_research",
        "بحث سوقي": "market_research",
    }

    for name, code in country_map.items():
        normalized_name = _normalize_arabic(name.lower())
        if normalized_name in normalized_intent:
            if name.lower() in ["مصر", "egypt"]:
                extracted["reporter"] = code
            elif name.lower() in ["الأردن", "jordan"]:
                extracted["partner"] = code

    for name, code in commodity_map.items():
        if name.lower() in normalized_intent:
            extracted.setdefault("commodities", []).append(code)

    if "commodities" in extracted:
        unique = list(dict.fromkeys(extracted["commodities"]))
        extracted["commodities"] = unique

    for name, request_type in request_type_map.items():
        if name.lower() in normalized_intent:
            extracted["request_type"] = request_type
            break

    return extracted


def build_qualified_query(intent: str, extracted: Dict[str, Any]) -> str:
    """Build a qualified query string from intent and extracted facts."""
    parts: list[str] = []
    request_type = extracted.get("request_type")
    if request_type:
        parts.append(request_type)
    commodities = extracted.get("commodities") or []
    if commodities:
        parts.extend(commodities)
    reporter = extracted.get("reporter")
    partner = extracted.get("partner")
    if reporter:
        parts.append(reporter)
    if partner:
        parts.append(partner)
    if parts:
        return f"{intent.strip()} {' '.join(parts)}"
    return intent.strip()


def normalize_research_context(context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Add safe aliases into research context for adapters that expect alternate keys."""
    original_context = parameters.get("context", {}) or {}

    if "country" not in context:
        if original_context.get("country"):
            context["country"] = original_context["country"]
        else:
            reporter = context.get("reporter")
            partner = context.get("partner")
            if reporter:
                context["country"] = reporter
            elif partner:
                context["country"] = partner

    if "area" not in context and original_context.get("area"):
        context["area"] = original_context["area"]

    return context
