import csv
import io
import uuid
from typing import Optional, Dict, Any, List

from app.services.base import connection, now_iso
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    _reportlab_available = True
except ImportError:
    _reportlab_available = False


_memory_provider = None
_knowledge_registry = None


def set_memory_provider(provider) -> None:
    global _memory_provider
    _memory_provider = provider


def set_knowledge_registry(registry) -> None:
    global _knowledge_registry
    _knowledge_registry = registry


def get_knowledge_registry():
    """Return the application-wide KnowledgeProviderRegistry, if set."""
    return _knowledge_registry


async def _get_knowledge_provider(source_id: str = "knowledge-graph"):
    if _knowledge_registry is None:
        return None
    return _knowledge_registry.get(source_id)


def _format_error(
    error_code: str,
    category: str,
    message: str,
    retryable: bool = False,
    caller_action: str = "",
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "error_code": error_code,
        "category": category,
        "message": message,
        "retryable": retryable,
        "caller_action": caller_action,
        "details": details,
        "correlation_id": correlation_id,
    }


def _get_entity_by_id(table: str, entity_id: int) -> Optional[Dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def _list_entities(table: str, limit: int = 100) -> List[Dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


async def _store_analysis_result(
    session_id: str,
    analysis_id: str,
    result: Dict[str, Any],
) -> None:
    if _memory_provider is None:
        return
    try:
        await _memory_provider.store(
            session_id=session_id,
            key=f"trade_intelligence:{analysis_id}",
            value=result,
            memory_type="context",
            importance=7,
        )
    except Exception:
        pass


async def _recall_analysis_result(
    session_id: str,
    analysis_id: str,
) -> Optional[Dict[str, Any]]:
    if _memory_provider is None:
        return None
    try:
        results = await _memory_provider.recall(
            session_id=session_id,
            query=f"trade_intelligence:{analysis_id}",
            limit=1,
        )
        if results:
            return results[0].get("value")
    except Exception:
        pass
    return None


def _calculate_confidence(
    data_quality_score: float,
    source_reliability_score: float,
    method_certainty_score: float,
) -> float:
    confidence = (
        0.40 * data_quality_score
        + 0.35 * source_reliability_score
        + 0.25 * method_certainty_score
    )
    return round(min(max(confidence, 0.0), 1.0), 2)


def _log_analysis_audit(
    current_user: Dict[str, Any],
    action: str,
    entity_type: str,
    entity_id: str,
    details: str = "",
    correlation_id: Optional[str] = None,
) -> None:
    if current_user is None:
        return
    try:
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            ),
        )
    except Exception:
        pass


async def perform_analysis(
    analysis_type: str,
    parameters: Dict[str, Any],
    current_user: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    requested_by = parameters.get("requested_by", "system")
    if analysis_type == "supplier":
        return await analyze_supplier(
            supplier_id=parameters.get("supplier_id"),
            analysis_type=parameters.get("analysis_type", "performance"),
            date_range=parameters.get("date_range"),
            requested_by=requested_by,
            current_user=current_user,
            correlation_id=correlation_id,
        )
    if analysis_type == "buyer":
        return await analyze_buyer(
            buyer_id=parameters.get("buyer_id"),
            analysis_type=parameters.get("analysis_type", "behavior"),
            date_range=parameters.get("date_range"),
            requested_by=requested_by,
            current_user=current_user,
            correlation_id=correlation_id,
        )
    if analysis_type == "trends":
        return await detect_trends(
            entity_type=parameters.get("entity_type", "supplier"),
            trend_parameters=parameters.get("trend_parameters", {}),
            requested_by=requested_by,
            current_user=current_user,
            correlation_id=correlation_id,
        )
    if analysis_type == "comparison":
        return await compare_entities(
            entity_ids=parameters.get("entity_ids", []),
            comparison_criteria=parameters.get("comparison_criteria", {}),
            requested_by=requested_by,
            current_user=current_user,
            correlation_id=correlation_id,
        )
    if analysis_type == "report":
        return await generate_report(
            analysis_ids=parameters.get("analysis_ids", []),
            report_type=parameters.get("report_type", "summary"),
            requested_by=requested_by,
            current_user=current_user,
            correlation_id=correlation_id,
        )
    return _format_error(
        error_code="invalid_analysis_type",
        category="validation",
        message=f"Unsupported analysis type: {analysis_type}",
        caller_action="Provide a valid analysis_type",
        correlation_id=correlation_id,
    )


async def analyze_supplier(
    supplier_id: int,
    analysis_type: str,
    date_range: Optional[dict],
    requested_by: str,
    current_user: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    analysis_id = str(uuid.uuid4())
    entity = _get_entity_by_id("suppliers", supplier_id)
    if not entity:
        return _format_error(
            error_code="supplier_not_found",
            category="not_found",
            message=f"Supplier {supplier_id} not found",
            caller_action="Verify supplier ID",
            correlation_id=correlation_id,
        )
    _log_analysis_audit(
        current_user=current_user,
        action="analyze",
        entity_type="trade_intelligence",
        entity_id=str(supplier_id),
        details=f"Supplier analysis requested: {analysis_type}",
        correlation_id=correlation_id,
    )
    knowledge_provider = await _get_knowledge_provider()
    knowledge_results: Dict[str, Any] = {"results": [], "confidence": None, "sources": []}
    if knowledge_provider is not None:
        try:
            knowledge_results = await knowledge_provider.query(
                query=f"supplier:{supplier_id} relationships",
                limit=10,
            )
        except Exception:
            knowledge_results = {"results": [], "confidence": None, "sources": []}
    non_null_fields = sum(1 for v in entity.values() if v is not None)
    total_fields = len(entity) if entity else 1
    data_quality_score = non_null_fields / total_fields if total_fields else 0.0
    source_reliability_score = 0.7 if knowledge_results.get("results") else 0.4
    sample_size = 1
    date_range_coverage = 1.0 if date_range else 0.5
    method_certainty_score = min(1.0, (sample_size / 10) * date_range_coverage)
    confidence = _calculate_confidence(
        data_quality_score=data_quality_score,
        source_reliability_score=source_reliability_score,
        method_certainty_score=method_certainty_score,
    )
    insight = {
        "finding": f"Supplier {entity.get('name', supplier_id)} analysis completed",
        "confidence": confidence,
        "evidence": [
            {
                "source_id": "entity_service",
                "data_point": {"supplier_id": supplier_id, "status": entity.get("status")},
                "timestamp": now_iso(),
            }
        ],
        "sources": ["entity_service"] + (knowledge_results.get("sources") or []),
        "analysis_id": analysis_id,
        "recommendations": [],
        "limitations": [],
    }
    output = {
        "analysis_id": analysis_id,
        "insights": [insight],
        "generated_at": now_iso(),
        "confidence": confidence,
        "data_sources": [
            {
                "source_type": "entity_service",
                "source_id": f"supplier:{supplier_id}",
                "accessed_at": now_iso(),
            }
        ],
    }
    await _store_analysis_result(session_id=str(current_user.get("id")), analysis_id=analysis_id, result=output)
    return output


async def analyze_buyer(
    buyer_id: int,
    analysis_type: str,
    date_range: Optional[dict],
    requested_by: str,
    current_user: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    analysis_id = str(uuid.uuid4())
    entity = _get_entity_by_id("customers", buyer_id)
    if not entity:
        return _format_error(
            error_code="buyer_not_found",
            category="not_found",
            message=f"Buyer {buyer_id} not found",
            caller_action="Verify buyer ID",
            correlation_id=correlation_id,
        )
    _log_analysis_audit(
        current_user=current_user,
        action="analyze",
        entity_type="trade_intelligence",
        entity_id=str(buyer_id),
        details=f"Buyer analysis requested: {analysis_type}",
        correlation_id=correlation_id,
    )
    knowledge_provider = await _get_knowledge_provider()
    knowledge_results: Dict[str, Any] = {"results": [], "confidence": None, "sources": []}
    if knowledge_provider is not None:
        try:
            knowledge_results = await knowledge_provider.query(
                query=f"customer:{buyer_id} relationships",
                limit=10,
            )
        except Exception:
            knowledge_results = {"results": [], "confidence": None, "sources": []}
    non_null_fields = sum(1 for v in entity.values() if v is not None)
    total_fields = len(entity) if entity else 1
    data_quality_score = non_null_fields / total_fields if total_fields else 0.0
    source_reliability_score = 0.7 if knowledge_results.get("results") else 0.4
    sample_size = 1
    date_range_coverage = 1.0 if date_range else 0.5
    method_certainty_score = min(1.0, (sample_size / 10) * date_range_coverage)
    confidence = _calculate_confidence(
        data_quality_score=data_quality_score,
        source_reliability_score=source_reliability_score,
        method_certainty_score=method_certainty_score,
    )
    insight = {
        "finding": f"Buyer {entity.get('name', buyer_id)} analysis completed",
        "confidence": confidence,
        "evidence": [
            {
                "source_id": "entity_service",
                "data_point": {"buyer_id": buyer_id, "status": entity.get("status")},
                "timestamp": now_iso(),
            }
        ],
        "sources": ["entity_service"] + (knowledge_results.get("sources") or []),
        "analysis_id": analysis_id,
        "recommendations": [],
        "limitations": [],
    }
    output = {
        "analysis_id": analysis_id,
        "insights": [insight],
        "generated_at": now_iso(),
        "confidence": confidence,
        "data_sources": [
            {
                "source_type": "entity_service",
                "source_id": f"customer:{buyer_id}",
                "accessed_at": now_iso(),
            }
        ],
    }
    await _store_analysis_result(session_id=str(current_user.get("id")), analysis_id=analysis_id, result=output)
    return output


async def detect_trends(
    entity_type: str,
    trend_parameters: dict,
    requested_by: str,
    current_user: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    analysis_id = str(uuid.uuid4())
    supported_types = ["supplier", "customer", "shipment", "invoice"]
    if entity_type not in supported_types:
        return _format_error(
            error_code="unsupported_entity_type",
            category="validation",
            message=f"Entity type '{entity_type}' is not supported for trend detection",
            caller_action="Use one of: supplier, customer, shipment, invoice",
            correlation_id=correlation_id,
        )
    _log_analysis_audit(
        current_user=current_user,
        action="detect_trends",
        entity_type="trade_intelligence",
        entity_id=entity_type,
        details=f"Trend detection requested for {entity_type}",
        correlation_id=correlation_id,
    )
    table_name = entity_type + "s" if not entity_type.endswith("s") else entity_type
    entities = _list_entities(table_name)
    if not entities:
        return _format_error(
            error_code="insufficient_data",
            category="dependency",
            message=f"No {entity_type} data available for trend detection",
            caller_action="Ensure entity data exists",
            correlation_id=correlation_id,
        )
    knowledge_provider = await _get_knowledge_provider()
    knowledge_results: Dict[str, Any] = {"results": [], "confidence": None, "sources": []}
    if knowledge_provider is not None:
        try:
            knowledge_results = await knowledge_provider.query(
                query=f"{entity_type} trends",
                context=trend_parameters,
                limit=10,
            )
        except Exception:
            knowledge_results = {"results": [], "confidence": None, "sources": []}
    data_quality_score = min(1.0, len(entities) / 10)
    source_reliability_score = 0.7 if knowledge_results.get("results") else 0.4
    method_certainty_score = 0.6
    confidence = _calculate_confidence(
        data_quality_score=data_quality_score,
        source_reliability_score=source_reliability_score,
        method_certainty_score=method_certainty_score,
    )
    output = {
        "analysis_id": analysis_id,
        "insights": [
            {
                "finding": f"Detected {len(entities)} {entity_type} records for trend analysis",
                "confidence": confidence,
                "evidence": [],
                "sources": ["entity_service"] + (knowledge_results.get("sources") or []),
                "analysis_id": analysis_id,
            }
        ],
        "generated_at": now_iso(),
        "confidence": confidence,
        "data_sources": [
            {
                "source_type": "entity_service",
                "source_id": entity_type,
                "accessed_at": now_iso(),
            }
        ],
    }
    await _store_analysis_result(session_id=str(current_user.get("id")), analysis_id=analysis_id, result=output)
    return output


async def compare_entities(
    entity_ids: List[int],
    comparison_criteria: dict,
    requested_by: str,
    current_user: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    analysis_id = str(uuid.uuid4())
    if len(entity_ids) < 2:
        return _format_error(
            error_code="insufficient_entities",
            category="validation",
            message="At least 2 entities are required for comparison",
            caller_action="Provide at least 2 entity IDs",
            correlation_id=correlation_id,
        )
    _log_analysis_audit(
        current_user=current_user,
        action="compare_entities",
        entity_type="trade_intelligence",
        entity_id=",".join(str(eid) for eid in entity_ids),
        details=f"Entity comparison requested for {entity_ids}",
        correlation_id=correlation_id,
    )
    entities = []
    for eid in entity_ids:
        for table in ["suppliers", "customers"]:
            entity = _get_entity_by_id(table, eid)
            if entity:
                entities.append({"id": eid, "table": table, "data": entity})
                break
    if len(entities) < 2:
        return _format_error(
            error_code="entities_not_found",
            category="not_found",
            message="Not enough entities found for comparison",
            caller_action="Verify entity IDs",
            correlation_id=correlation_id,
        )
    data_quality_score = min(1.0, len(entities) / 5)
    source_reliability_score = 0.5
    method_certainty_score = 0.6
    confidence = _calculate_confidence(
        data_quality_score=data_quality_score,
        source_reliability_score=source_reliability_score,
        method_certainty_score=method_certainty_score,
    )
    comparison_results = []
    for entity in entities:
        comparison_results.append({
            "entity_id": entity["id"],
            "entity_type": entity["table"].rstrip("s"),
            "metrics": {
                "name": entity["data"].get("name") or entity["data"].get("company_name"),
                "status": entity["data"].get("status"),
                "country": entity["data"].get("country"),
            },
        })
    output = {
        "comparison_id": analysis_id,
        "results": comparison_results,
        "recommendations": [],
        "generated_at": now_iso(),
        "entity_ids": entity_ids,
        "criteria": comparison_criteria,
        "confidence": confidence,
    }
    return output


async def generate_report(
    analysis_ids: List[str],
    report_type: str,
    requested_by: str,
    current_user: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    report_id = str(uuid.uuid4())
    if not analysis_ids:
        return _format_error(
            error_code="no_analysis_ids",
            category="validation",
            message="At least one analysis ID is required to generate a report",
            caller_action="Provide valid analysis IDs",
            correlation_id=correlation_id,
        )
    _log_analysis_audit(
        current_user=current_user,
        action="generate_report",
        entity_type="trade_intelligence",
        entity_id=report_id,
        details=f"Report generation requested: {report_type} for {len(analysis_ids)} analyses",
        correlation_id=correlation_id,
    )
    sections = ["Executive Summary", "Analysis Details", "Recommendations"]
    if report_type == "supplier":
        sections = ["Executive Summary", "Supplier Metrics", "Trends", "Recommendations"]
    elif report_type == "buyer":
        sections = ["Executive Summary", "Customer Segments", "Behavior Patterns", "Recommendations"]
    elif report_type == "trends":
        sections = ["Executive Summary", "Trends Detected", "Statistical Summary", "Recommendations"]
    elif report_type == "comparison":
        sections = ["Executive Summary", "Entity Comparison", "Gap Analysis", "Recommendations"]

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["section", "detail"])
    for section in sections:
        writer.writerow([section, f"{report_type} report section"])
    csv_content = csv_buffer.getvalue()

    pdf_content = b""
    if _reportlab_available:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles["Title"]),
            Paragraph(f"Generated at: {now_iso()}", styles["Normal"]),
            Paragraph(f"Analysis count: {len(analysis_ids)}", styles["Normal"]),
        ]
        for section in sections:
            story.append(Paragraph(section, styles["Heading2"]))
        table_data = [["Section", "Status"]] + [[section, "Included"] for section in sections]
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        doc.build(story)
        pdf_content = pdf_buffer.getvalue()

    output = {
        "report_id": report_id,
        "report_type": report_type,
        "format": "csv",
        "sections": sections,
        "content": {
            "analysis_ids": analysis_ids,
            "summary": f"Report generated for {len(analysis_ids)} analyses",
            "sections": sections,
            "csv": csv_content,
            "pdf": pdf_content.decode("latin-1") if pdf_content else "",
        },
        "generated_at": now_iso(),
        "metadata": {
            "requested_by": requested_by,
            "analysis_count": len(analysis_ids),
        },
    }
    await _store_analysis_result(
        session_id=str(current_user.get("id")),
        analysis_id=report_id,
        result=output,
    )
    return output
