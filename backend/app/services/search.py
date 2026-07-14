from typing import Optional

from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.base import connection, build_list_query


def _calculate_relevance(title: Optional[str], query: str) -> float:
    if not title or not query:
        return 0.0
    title_lower = title.lower()
    query_lower = query.lower()
    if title_lower == query_lower:
        return 1.0
    if title_lower.startswith(query_lower):
        return 0.8
    if query_lower in title_lower:
        return 0.6
    return 0.0


def _normalize_customer(row: dict, query: str) -> SearchResult:
    title = row.get("name") or row.get("company_name") or ""
    return SearchResult(
        entity_type="customer",
        id=row["id"],
        title=title,
        subtitle=row.get("contact_person"),
        url=f"/customers/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_supplier(row: dict, query: str) -> SearchResult:
    title = row.get("name") or ""
    return SearchResult(
        entity_type="supplier",
        id=row["id"],
        title=title,
        subtitle=row.get("contact_person"),
        url=f"/suppliers/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_shipment(row: dict, query: str) -> SearchResult:
    title = row.get("tracking_number") or ""
    return SearchResult(
        entity_type="shipment",
        id=row["id"],
        title=title,
        subtitle=row.get("status"),
        url=f"/shipments/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_invoice(row: dict, query: str) -> SearchResult:
    title = row.get("invoice_number") or f"Invoice #{row['id']}"
    return SearchResult(
        entity_type="invoice",
        id=row["id"],
        title=title,
        subtitle=row.get("customer_name"),
        url=f"/invoices/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_declaration(row: dict, query: str) -> SearchResult:
    title = row.get("declaration_number") or f"Declaration #{row['id']}"
    return SearchResult(
        entity_type="declaration",
        id=row["id"],
        title=title,
        subtitle=row.get("customer_name"),
        url=f"/customs/declarations/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_document(row: dict, query: str) -> SearchResult:
    title = row.get("title") or row.get("file_name") or ""
    return SearchResult(
        entity_type="document",
        id=row["id"],
        title=title,
        subtitle=row.get("document_type"),
        url=f"/documents/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_resource(row: dict, query: str) -> SearchResult:
    title = row.get("title") or ""
    return SearchResult(
        entity_type="resource",
        id=row["id"],
        title=title,
        subtitle=row.get("resource_type"),
        url=row.get("url") or f"/resources/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_hs_code(row: dict, query: str) -> SearchResult:
    title = row.get("code") or ""
    return SearchResult(
        entity_type="hs_code",
        id=row["id"],
        title=title,
        subtitle=row.get("description"),
        url=f"/customs/hs-codes/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


def _normalize_eta_connector(row: dict, query: str) -> SearchResult:
    title = row.get("name") or f"Connector #{row['id']}"
    return SearchResult(
        entity_type="eta_connector",
        id=row["id"],
        title=title,
        subtitle=row.get("environment"),
        url=f"/eta/connectors/{row['id']}",
        relevance=_calculate_relevance(title, query),
    )


_ENTITY_SEARCH = {
    "customer": {
        "table": "customers",
        "search_fields": ["name", "name_en", "email", "phone"],
        "normalize": _normalize_customer,
    },
    "supplier": {
        "table": "suppliers",
        "search_fields": ["name", "name_en", "email", "phone"],
        "normalize": _normalize_supplier,
    },
    "shipment": {
        "table": "shipments",
        "search_fields": ["tracking_number", "origin", "destination", "reference", "awb_number"],
        "normalize": _normalize_shipment,
    },
    "invoice": {
        "table": "invoices",
        "search_fields": ["invoice_number", "internal_id", "eta_uuid", "eta_submission_id", "status", "notes"],
        "normalize": _normalize_invoice,
    },
    "declaration": {
        "table": "customs_declarations",
        "search_fields": ["declaration_number", "origin_country", "destination_country", "status"],
        "normalize": _normalize_declaration,
    },
    "document": {
        "table": "documents",
        "search_fields": ["title", "file_name", "file_type", "entity_type"],
        "normalize": _normalize_document,
    },
    "resource": {
        "table": "resources",
        "search_fields": ["title", "title_ar", "description", "description_ar"],
        "normalize": _normalize_resource,
    },
    "hs_code": {
        "table": "hs_codes",
        "search_fields": ["code", "description", "description_ar"],
        "normalize": _normalize_hs_code,
    },
    "eta_connector": {
        "table": "eta_connectors",
        "search_fields": ["name", "client_id", "environment", "status"],
        "normalize": _normalize_eta_connector,
    },
}


def search_all(query: str, entity_type: Optional[str] = None) -> SearchResponse:
    if not query:
        return SearchResponse(results=[], query=query, total=0)

    entities = [_ENTITY_SEARCH[entity_type]] if entity_type in _ENTITY_SEARCH else list(_ENTITY_SEARCH.values())
    results = []

    for entity in entities:
        q, params = build_list_query(
            entity["table"],
            search_fields=entity["search_fields"],
            search=query,
            limit=50,
        )
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute(q, params)
            rows = cursor.fetchall()
            for row in rows:
                results.append(entity["normalize"](dict(row), query))

    results.sort(key=lambda item: item.relevance or 0, reverse=True)
    return SearchResponse(results=results, query=query, total=len(results))
