from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import pytest

from app.services.trade_intelligence import (
    _calculate_confidence,
    _format_error,
    _get_entity_by_id,
    _list_entities,
    set_memory_provider,
    set_knowledge_registry,
    analyze_supplier,
    analyze_buyer,
    detect_trends,
    compare_entities,
    generate_report,
    perform_analysis,
    _log_analysis_audit,
    _store_analysis_result,
    _recall_analysis_result,
)


# ========== Helpers ==========


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def _make_supplier_row(supplier_id=1, name="Test Supplier", status="active", country="Egypt"):
    return {
        "id": supplier_id,
        "name": name,
        "status": status,
        "country": country,
        "contact_person": None,
        "email": None,
        "phone": None,
        "address": None,
        "city": None,
        "tax_id": None,
        "commercial_registry": None,
        "certificates": None,
        "notes": None,
        "created_at": "2026-07-20T00:00:00",
    }


def _make_customer_row(customer_id=1, name="Test Customer", status="active"):
    return {
        "id": customer_id,
        "name": name,
        "status": status,
        "contact_person": None,
        "email": None,
        "phone": None,
        "address": None,
        "city": None,
        "country": "Egypt",
        "tax_id": None,
        "import_license": None,
        "category": None,
        "notes": None,
        "created_at": "2026-07-20T00:00:00",
    }


def _make_user(user_id=1):
    return {"id": user_id, "username": "testuser"}


# ========== _calculate_confidence Tests ==========


class TestCalculateConfidence:
    def test_returns_weighted_average(self):
        result = _calculate_confidence(1.0, 1.0, 1.0)
        assert result == 1.0

    def test_returns_zero_for_all_zeros(self):
        result = _calculate_confidence(0.0, 0.0, 0.0)
        assert result == 0.0

    def test_weights_data_quality_40_percent(self):
        result = _calculate_confidence(1.0, 0.0, 0.0)
        assert result == 0.4

    def test_weights_source_reliability_35_percent(self):
        result = _calculate_confidence(0.0, 1.0, 0.0)
        assert result == 0.35

    def test_weights_method_certainty_25_percent(self):
        result = _calculate_confidence(0.0, 0.0, 1.0)
        assert result == 0.25

    def test_clamps_to_max_1(self):
        result = _calculate_confidence(2.0, 2.0, 2.0)
        assert result == 1.0

    def test_clamps_to_min_0(self):
        result = _calculate_confidence(-1.0, -1.0, -1.0)
        assert result == 0.0

    def test_rounds_to_two_decimals(self):
        result = _calculate_confidence(0.1, 0.1, 0.1)
        assert len(str(result).split(".")[-1]) <= 2


# ========== _format_error Tests ==========


class TestFormatError:
    def test_basic_error(self):
        result = _format_error("test_code", "validation", "test message")
        assert result["error_code"] == "test_code"
        assert result["category"] == "validation"
        assert result["message"] == "test message"
        assert result["retryable"] is False
        assert result["caller_action"] == ""

    def test_retryable_flag(self):
        result = _format_error("code", "dependency", "msg", retryable=True)
        assert result["retryable"] is True

    def test_caller_action(self):
        result = _format_error("code", "internal", "msg", caller_action="retry")
        assert result["caller_action"] == "retry"

    def test_details(self):
        details = {"key": "value"}
        result = _format_error("code", "validation", "msg", details=details)
        assert result["details"] == details

    def test_correlation_id(self):
        result = _format_error("code", "validation", "msg", correlation_id="abc-123")
        assert result["correlation_id"] == "abc-123"

    def test_all_fields(self):
        result = _format_error(
            error_code="e",
            category="dependency",
            message="m",
            retryable=True,
            caller_action="act",
            details={"d": 1},
            correlation_id="cid",
        )
        assert result == {
            "error_code": "e",
            "category": "dependency",
            "message": "m",
            "retryable": True,
            "caller_action": "act",
            "details": {"d": 1},
            "correlation_id": "cid",
        }


# ========== _get_entity_by_id Tests ==========


class TestGetEntityById:
    def test_returns_row_when_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = _get_entity_by_id("suppliers", 1)

        assert result["id"] == 1
        assert result["name"] == "Test Supplier"

    def test_returns_none_when_not_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = _get_entity_by_id("suppliers", 999)

        assert result is None

    def test_uses_parameterized_query(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            _get_entity_by_id("suppliers", 42)

        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        assert args[0] == "SELECT * FROM suppliers WHERE id = ?"
        assert args[1] == (42,)


# ========== _list_entities Tests ==========


class TestListEntities:
    def test_returns_rows_as_list(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_make_supplier_row(), _make_supplier_row(2)]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = _list_entities("suppliers")

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_respects_limit(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            _list_entities("suppliers", limit=5)

        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        assert args[0] == "SELECT * FROM suppliers LIMIT ?"
        assert args[1] == (5,)

    def test_returns_empty_list_when_no_rows(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = _list_entities("suppliers")

        assert result == []


# ========== Memory Provider Tests ==========


class TestMemoryProviderIntegration:
    def test_set_memory_provider(self):
        mock_provider = MagicMock()
        set_memory_provider(mock_provider)
        from app.services.trade_intelligence import _memory_provider
        assert _memory_provider is mock_provider

    def test_set_knowledge_registry(self):
        mock_registry = MagicMock()
        set_knowledge_registry(mock_registry)
        from app.services.trade_intelligence import _knowledge_registry
        assert _knowledge_registry is mock_registry

    def test_store_calls_memory_provider(self):
        mock_provider = AsyncMock()
        set_memory_provider(mock_provider)

        asyncio.run(_store_analysis_result("session-1", "analysis-1", {"key": "value"}))

        mock_provider.store.assert_called_once()
        call_kwargs = mock_provider.store.call_args[1]
        assert call_kwargs["session_id"] == "session-1"
        assert call_kwargs["key"] == "trade_intelligence:analysis-1"
        assert call_kwargs["memory_type"] == "context"
        assert call_kwargs["importance"] == 7

    def test_recall_calls_memory_provider(self):
        mock_provider = AsyncMock()
        mock_provider.recall.return_value = [{"key": "trade_intelligence:analysis-1", "value": {"result": "ok"}}]
        set_memory_provider(mock_provider)

        result = asyncio.run(_recall_analysis_result("session-1", "analysis-1"))

        mock_provider.recall.assert_called_once_with(session_id="session-1", query="trade_intelligence:analysis-1", limit=1)
        assert result == {"result": "ok"}

    def test_recall_returns_none_when_no_results(self):
        mock_provider = AsyncMock()
        mock_provider.recall.return_value = []
        set_memory_provider(mock_provider)

        result = asyncio.run(_recall_analysis_result("session-1", "analysis-1"))

        assert result is None

    def test_store_handles_memory_provider_none(self):
        set_memory_provider(None)
        result = asyncio.run(_store_analysis_result("session-1", "analysis-1", {}))
        assert result is None

    def test_recall_handles_memory_provider_none(self):
        set_memory_provider(None)
        result = asyncio.run(_recall_analysis_result("session-1", "analysis-1"))
        assert result is None


# ========== _log_analysis_audit Tests ==========


class TestLogAnalysisAudit:
    def test_calls_log_audit(self):
        mock_current_user = _make_user()
        with patch("app.services.trade_intelligence.log_audit") as mock_log:
            _log_analysis_audit(
                current_user=mock_current_user,
                action="analyze",
                entity_type="trade_intelligence",
                entity_id="1",
                details="test",
            )
            mock_log.assert_called_once()

    def test_skips_when_no_current_user(self):
        with patch("app.services.trade_intelligence.log_audit") as mock_log:
            _log_analysis_audit(
                current_user=None,
                action="analyze",
                entity_type="trade_intelligence",
                entity_id="1",
            )
            mock_log.assert_not_called()

    def test_passes_correct_parameters(self):
        mock_current_user = _make_user()
        with patch("app.services.trade_intelligence.log_audit") as mock_log:
            _log_analysis_audit(
                current_user=mock_current_user,
                action="test_action",
                entity_type="trade_intelligence",
                entity_id="42",
                details="test details",
            )
            call_args = mock_log.call_args
            assert call_args[1]["current_user"] == mock_current_user
            assert call_args[1]["data"].action == "test_action"
            assert call_args[1]["data"].entity_type == "trade_intelligence"
            assert call_args[1]["data"].entity_id == 42
            assert call_args[1]["data"].details == "test details"


# ========== analyze_supplier Tests ==========


class TestAnalyzeSupplier:
    def test_returns_error_when_supplier_not_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_supplier(
                supplier_id=999,
                analysis_type="performance",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert result["error_code"] == "supplier_not_found"
        assert result["category"] == "not_found"

    def test_returns_insight_when_supplier_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_supplier(
                supplier_id=1,
                analysis_type="performance",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result
        assert "insights" in result
        assert "confidence" in result
        assert result["confidence"] >= 0.0
        assert result["confidence"] <= 1.0

    def test_stores_result_in_memory(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)
        mock_memory = AsyncMock()

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._memory_provider", mock_memory):
                result = asyncio.run(analyze_supplier(
                    supplier_id=1,
                    analysis_type="performance",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        mock_memory.store.assert_called_once()
        call_kwargs = mock_memory.store.call_args[1]
        assert call_kwargs["key"] == f"trade_intelligence:{result['analysis_id']}"

    def test_logs_audit(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence.log_audit") as mock_log:
                asyncio.run(analyze_supplier(
                    supplier_id=1,
                    analysis_type="performance",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))
                mock_log.assert_called_once()

    def test_includes_knowledge_results_when_available(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        mock_knowledge = AsyncMock()
        mock_knowledge.query.return_value = {
            "results": [{"relationship": "related_to", "target": "customer:1"}],
            "confidence": 0.8,
            "sources": ["knowledge-graph"],
        }

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._knowledge_registry") as mock_registry:
                mock_registry.get.return_value = mock_knowledge
                result = asyncio.run(analyze_supplier(
                    supplier_id=1,
                    analysis_type="performance",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        assert "knowledge-graph" in result["insights"][0]["sources"]

    def test_graceful_degradation_without_knowledge(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._knowledge_registry", None):
                result = asyncio.run(analyze_supplier(
                    supplier_id=1,
                    analysis_type="performance",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        assert "analysis_id" in result
        assert "insights" in result

    def test_confidence_calculated_with_date_range(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_supplier(
                supplier_id=1,
                analysis_type="performance",
                date_range={"start": "2024-01-01", "end": "2024-12-31"},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert result["confidence"] >= 0.0
        assert result["confidence"] <= 1.0


# ========== analyze_buyer Tests ==========


class TestAnalyzeBuyer:
    def test_returns_error_when_buyer_not_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_buyer(
                buyer_id=999,
                analysis_type="behavior",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert result["error_code"] == "buyer_not_found"
        assert result["category"] == "not_found"

    def test_returns_insight_when_buyer_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_customer_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_buyer(
                buyer_id=1,
                analysis_type="behavior",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result
        assert "insights" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_stores_result_in_memory(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_customer_row()
        mock_conn = _mock_connection(mock_cursor)
        mock_memory = AsyncMock()

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._memory_provider", mock_memory):
                result = asyncio.run(analyze_buyer(
                    buyer_id=1,
                    analysis_type="behavior",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        mock_memory.store.assert_called_once()

    def test_logs_audit(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_customer_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence.log_audit") as mock_log:
                asyncio.run(analyze_buyer(
                    buyer_id=1,
                    analysis_type="behavior",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))
                mock_log.assert_called_once()

    def test_graceful_degradation_without_knowledge(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_customer_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._knowledge_registry", None):
                result = asyncio.run(analyze_buyer(
                    buyer_id=1,
                    analysis_type="behavior",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        assert "analysis_id" in result


# ========== detect_trends Tests ==========


class TestDetectTrends:
    def test_returns_trends_with_data(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_make_supplier_row(), _make_supplier_row(2)]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(detect_trends(
                entity_type="supplier",
                trend_parameters={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result
        assert "insights" in result
        assert "confidence" in result

    def test_returns_error_for_unsupported_entity_type(self):
        result = asyncio.run(detect_trends(
            entity_type="unsupported",
            trend_parameters={},
            requested_by="test",
            current_user=_make_user(),
        ))

        assert result["error_code"] == "unsupported_entity_type"
        assert result["category"] == "validation"

    def test_returns_error_when_no_data(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(detect_trends(
                entity_type="supplier",
                trend_parameters={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert result["error_code"] == "insufficient_data"
        assert result["category"] == "dependency"

    def test_logs_audit(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_make_supplier_row()]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._log_analysis_audit") as mock_audit:
                asyncio.run(detect_trends(
                    entity_type="supplier",
                    trend_parameters={},
                    requested_by="test",
                    current_user=_make_user(),
                ))
                mock_audit.assert_called_once()

    def test_supports_customer_entity_type(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_make_customer_row()]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(detect_trends(
                entity_type="customer",
                trend_parameters={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result

    def test_supports_shipment_entity_type(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "tracking_number": "TRACK1", "status": "pending"}
        ]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(detect_trends(
                entity_type="shipment",
                trend_parameters={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result


# ========== compare_entities Tests ==========


class TestCompareEntities:
    def test_returns_error_for_single_entity(self):
        result = asyncio.run(compare_entities(
            entity_ids=[1],
            comparison_criteria={},
            requested_by="test",
            current_user=_make_user(),
        ))

        assert result["error_code"] == "insufficient_entities"
        assert result["category"] == "validation"

    def test_returns_comparison_for_suppliers(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [_make_supplier_row(1), _make_supplier_row(2)]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(compare_entities(
                entity_ids=[1, 2],
                comparison_criteria={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "comparison_id" in result
        assert len(result["results"]) == 2
        assert "confidence" in result

    def test_returns_error_when_entities_not_found(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(compare_entities(
                entity_ids=[1, 2],
                comparison_criteria={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert result["error_code"] == "entities_not_found"
        assert result["category"] == "not_found"

    def test_logs_audit(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [_make_supplier_row(1), _make_supplier_row(2)]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._log_analysis_audit") as mock_audit:
                asyncio.run(compare_entities(
                    entity_ids=[1, 2],
                    comparison_criteria={},
                    requested_by="test",
                    current_user=_make_user(),
                ))
                mock_audit.assert_called_once()


# ========== generate_report Tests ==========


class TestGenerateReport:
    def test_returns_error_for_empty_analysis_ids(self):
        result = asyncio.run(generate_report(
            analysis_ids=[],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert result["error_code"] == "no_analysis_ids"
        assert result["category"] == "validation"

    def test_generates_report_with_default_sections(self):
        result = asyncio.run(generate_report(
            analysis_ids=["analysis-1"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert "report_id" in result
        assert result["report_type"] == "summary"
        assert "sections" in result
        assert "content" in result
        assert result["format"] == "csv"
        assert "csv" in result["content"]
        assert "pdf" in result["content"]

    def test_generates_supplier_report_sections(self):
        result = asyncio.run(generate_report(
            analysis_ids=["analysis-1"],
            report_type="supplier",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert "Executive Summary" in result["sections"]
        assert "Supplier Metrics" in result["sections"]

    def test_generates_buyer_report_sections(self):
        result = asyncio.run(generate_report(
            analysis_ids=["analysis-1"],
            report_type="buyer",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert "Customer Segments" in result["sections"]

    def test_generates_comparison_report_sections(self):
        result = asyncio.run(generate_report(
            analysis_ids=["analysis-1"],
            report_type="comparison",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert "Entity Comparison" in result["sections"]

    def test_stores_result_in_memory(self):
        mock_memory = AsyncMock()
        with patch("app.services.trade_intelligence._memory_provider", mock_memory):
            result = asyncio.run(generate_report(
                analysis_ids=["analysis-1"],
                report_type="summary",
                requested_by="test",
                current_user=_make_user(),
            ))

        mock_memory.store.assert_called_once()
        call_kwargs = mock_memory.store.call_args[1]
        assert call_kwargs["key"] == f"trade_intelligence:{result['report_id']}"

    def test_logs_audit(self):
        with patch("app.services.trade_intelligence._log_analysis_audit") as mock_audit:
            asyncio.run(generate_report(
                analysis_ids=["analysis-1"],
                report_type="summary",
                requested_by="test",
                current_user=_make_user(),
            ))
            mock_audit.assert_called_once()

    def test_includes_metadata(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1", "a2", "a3"],
            report_type="summary",
            requested_by="test_user",
            current_user=_make_user(),
        ))

        assert result["metadata"]["requested_by"] == "test_user"
        assert result["metadata"]["analysis_count"] == 3


# ========== perform_analysis Dispatcher Tests ==========


class TestPerformAnalysis:
    def test_dispatches_to_supplier_analysis(self):
        with patch("app.services.trade_intelligence.analyze_supplier", new_callable=AsyncMock) as mock_supplier:
            mock_supplier.return_value = {"analysis_id": "test-1"}
            result = asyncio.run(perform_analysis(
                analysis_type="supplier",
                parameters={"supplier_id": 1, "analysis_type": "performance", "requested_by": "test"},
                current_user=_make_user(),
            ))
            mock_supplier.assert_called_once()

    def test_dispatches_to_buyer_analysis(self):
        with patch("app.services.trade_intelligence.analyze_buyer", new_callable=AsyncMock) as mock_buyer:
            mock_buyer.return_value = {"analysis_id": "test-1"}
            result = asyncio.run(perform_analysis(
                analysis_type="buyer",
                parameters={"buyer_id": 1, "analysis_type": "behavior", "requested_by": "test"},
                current_user=_make_user(),
            ))
            mock_buyer.assert_called_once()

    def test_dispatches_to_trends(self):
        with patch("app.services.trade_intelligence.detect_trends", new_callable=AsyncMock) as mock_trends:
            mock_trends.return_value = {"analysis_id": "test-1"}
            result = asyncio.run(perform_analysis(
                analysis_type="trends",
                parameters={"entity_type": "supplier", "trend_parameters": {}, "requested_by": "test"},
                current_user=_make_user(),
            ))
            mock_trends.assert_called_once()

    def test_dispatches_to_comparison(self):
        with patch("app.services.trade_intelligence.compare_entities", new_callable=AsyncMock) as mock_compare:
            mock_compare.return_value = {"comparison_id": "test-1"}
            result = asyncio.run(perform_analysis(
                analysis_type="comparison",
                parameters={"entity_ids": [1, 2], "comparison_criteria": {}, "requested_by": "test"},
                current_user=_make_user(),
            ))
            mock_compare.assert_called_once()

    def test_dispatches_to_report(self):
        with patch("app.services.trade_intelligence.generate_report", new_callable=AsyncMock) as mock_report:
            mock_report.return_value = {"report_id": "test-1"}
            result = asyncio.run(perform_analysis(
                analysis_type="report",
                parameters={"analysis_ids": ["a1"], "report_type": "summary", "requested_by": "test"},
                current_user=_make_user(),
            ))
            mock_report.assert_called_once()

    def test_returns_error_for_unsupported_type(self):
        result = asyncio.run(perform_analysis(
            analysis_type="unsupported",
            parameters={},
            current_user=_make_user(),
        ))

        assert result["error_code"] == "invalid_analysis_type"
        assert result["category"] == "validation"


# ========== Graceful Degradation Tests ==========


class TestGracefulDegradation:
    def test_analyze_supplier_without_memory_provider(self):
        set_memory_provider(None)
        set_knowledge_registry(None)

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_supplier(
                supplier_id=1,
                analysis_type="performance",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result
        assert "insights" in result

    def test_analyze_buyer_without_memory_provider(self):
        set_memory_provider(None)
        set_knowledge_registry(None)

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_customer_row()
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(analyze_buyer(
                buyer_id=1,
                analysis_type="behavior",
                date_range=None,
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result
        assert "insights" in result

    def test_detect_trends_without_knowledge_provider(self):
        set_memory_provider(None)
        set_knowledge_registry(None)

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_make_supplier_row()]
        mock_conn = _mock_connection(mock_cursor)

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            result = asyncio.run(detect_trends(
                entity_type="supplier",
                trend_parameters={},
                requested_by="test",
                current_user=_make_user(),
            ))

        assert "analysis_id" in result

    def test_knowledge_provider_failure_does_not_break_analysis(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _make_supplier_row()
        mock_conn = _mock_connection(mock_cursor)

        mock_knowledge = AsyncMock()
        mock_knowledge.query.side_effect = Exception("Knowledge provider down")

        with patch("app.services.trade_intelligence.connection", return_value=mock_conn):
            with patch("app.services.trade_intelligence._knowledge_registry") as mock_registry:
                mock_registry.get.return_value = mock_knowledge
                result = asyncio.run(analyze_supplier(
                    supplier_id=1,
                    analysis_type="performance",
                    date_range=None,
                    requested_by="test",
                    current_user=_make_user(),
                ))

        assert "analysis_id" in result


# ========== Report Generation Tests ==========


class TestReportGeneration:
    def test_csv_content_generated(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        csv_content = result["content"]["csv"]
        assert "section" in csv_content
        assert "detail" in csv_content

    def test_pdf_content_generated(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        pdf_content = result["content"]["pdf"]
        assert isinstance(pdf_content, str)
        assert len(pdf_content) > 0

    def test_report_format_is_csv(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert result["format"] == "csv"

    def test_report_generated_at_timestamp(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert "generated_at" in result
        assert isinstance(result["generated_at"], str)

    def test_report_metadata_includes_analysis_count(self):
        result = asyncio.run(generate_report(
            analysis_ids=["a1", "a2", "a3"],
            report_type="summary",
            requested_by="test",
            current_user=_make_user(),
        ))

        assert result["metadata"]["analysis_count"] == 3
