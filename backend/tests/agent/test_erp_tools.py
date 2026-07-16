import pytest
import asyncio
from unittest.mock import MagicMock, patch
from app.agent.tools.registry import tool_registry
from app.agent.tools.base import ToolSideEffect
from app.agent.tools.erp_tools import (
    ShippingGetRatesTool,
    ShippingCreateShipmentTool,
    ShippingPrintLabelTool,
    EtaSubmitInvoiceTool,
    EtaCheckStatusTool,
    CustomsGetDeclarationsTool,
    CustomsFileDeclarationTool,
    DocumentsGenerateTool,
    DocumentsUploadTool,
    SearchGlobalTool,
    DashboardGetStatsTool,
    NotificationsSendTool,
    WorkflowGetStateTool,
    WorkflowTransitionTool,
)


class TestERPToolRegistration:
    """Verify all ERP tools are registered."""

    def test_all_erp_tools_registered(self):
        registered_names = [t["tool_name"] for t in tool_registry.list_tools()]
        expected_tools = [
            "shipping_get_rates",
            "shipping_create_shipment",
            "shipping_print_label",
            "eta_submit_invoice",
            "eta_check_status",
            "customs_get_declarations",
            "customs_file_declaration",
            "documents_generate",
            "documents_upload",
            "search_global",
            "dashboard_get_stats",
            "notifications_send",
            "workflow_get_state",
            "workflow_transition",
        ]
        for tool_name in expected_tools:
            assert tool_name in registered_names, f"{tool_name} not registered"

    def test_tool_count(self):
        tools = tool_registry.list_tools()
        assert len(tools) >= 14  # 14 ERP tools + test_tool


class TestShippingTools:
    """Tests for shipping tool wrappers."""

    def test_shipping_get_rates_metadata(self):
        tool = ShippingGetRatesTool()
        assert tool.tool_name == "shipping_get_rates"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True
        assert tool.auth_required is True

    @patch("app.services.shipping.fetch_rates")
    def test_shipping_get_rates_execute(self, mock_fetch_rates):
        mock_fetch_rates.return_value = [{"carrier": "DHL", "cost": 25.0}]
        tool = ShippingGetRatesTool()
        parameters = {
            "origin": "EG Cairo",
            "destination": "DE Berlin",
            "weight": 1.0,
        }
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert "rates" in result.data

    def test_shipping_create_shipment_metadata(self):
        tool = ShippingCreateShipmentTool()
        assert tool.tool_name == "shipping_create_shipment"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is False

    @patch("app.services.shipping.create_shipment")
    def test_shipping_create_shipment_execute(self, mock_create_shipment):
        mock_create_shipment.return_value = {"shipment_id": 1, "tracking_number": "TRACK123"}
        tool = ShippingCreateShipmentTool()
        parameters = {
            "provider": "DHL",
            "service": "express",
            "origin": "EG Cairo",
            "destination": "DE Berlin",
            "weight": 1.0,
        }
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"
        assert result.data["shipment_id"] == 1

    def test_shipping_print_label_metadata(self):
        tool = ShippingPrintLabelTool()
        assert tool.tool_name == "shipping_print_label"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True

    @patch("app.services.shipping.get_label")
    def test_shipping_print_label_execute(self, mock_get_label):
        mock_get_label.return_value = {"label_url": "/storage/labels/label_1.pdf"}
        tool = ShippingPrintLabelTool()
        parameters = {"shipment_id": 1}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert "label_url" in result.data


class TestEtaTools:
    """Tests for ETA tool wrappers."""

    def test_eta_submit_invoice_metadata(self):
        tool = EtaSubmitInvoiceTool()
        assert tool.tool_name == "eta_submit_invoice"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is True

    @patch("app.services.eta.submit_invoice_to_eta")
    def test_eta_submit_invoice_execute(self, mock_submit):
        mock_submit.return_value = {"status": "submitted", "submission_id": "SUB123"}
        tool = EtaSubmitInvoiceTool()
        parameters = {"invoice_id": 1, "connector_id": 1}
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"
        assert result.data["submission_id"] == "SUB123"

    def test_eta_check_status_metadata(self):
        tool = EtaCheckStatusTool()
        assert tool.tool_name == "eta_check_status"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True

    @patch("app.services.eta.get_eta_invoice_status")
    def test_eta_check_status_execute(self, mock_status):
        mock_status.return_value = {"status": "accepted"}
        tool = EtaCheckStatusTool()
        parameters = {"invoice_id": 1}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert result.data["status"] == "accepted"


class TestCustomsTools:
    """Tests for customs tool wrappers."""

    def test_customs_get_declarations_metadata(self):
        tool = CustomsGetDeclarationsTool()
        assert tool.tool_name == "customs_get_declarations"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True

    @patch("app.services.customs.list_declarations")
    def test_customs_get_declarations_execute(self, mock_list):
        mock_list.return_value = [{"id": 1, "status": "draft"}]
        tool = CustomsGetDeclarationsTool()
        parameters = {}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert "declarations" in result.data

    def test_customs_file_declaration_metadata(self):
        tool = CustomsFileDeclarationTool()
        assert tool.tool_name == "customs_file_declaration"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is False

    @patch("app.services.customs.submit_declaration")
    def test_customs_file_declaration_execute(self, mock_submit):
        mock_submit.return_value = {"status": "submitted"}
        tool = CustomsFileDeclarationTool()
        parameters = {"declaration_id": 1}
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"


class TestDocumentTools:
    """Tests for document tool wrappers."""

    def test_documents_generate_metadata(self):
        tool = DocumentsGenerateTool()
        assert tool.tool_name == "documents_generate"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is False

    @patch("app.services.document.create_document")
    def test_documents_generate_execute(self, mock_create):
        mock_create.return_value = {"id": 1, "title": "Test Doc"}
        tool = DocumentsGenerateTool()
        parameters = {"title": "Test Doc", "document_type": "invoice", "content": "Content"}
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"
        assert result.data["id"] == 1

    def test_documents_upload_metadata(self):
        tool = DocumentsUploadTool()
        assert tool.tool_name == "documents_upload"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is False

    @patch("app.services.document.upload_document")
    def test_documents_upload_execute(self, mock_upload):
        mock_upload.return_value = {"id": 1, "filename": "test.pdf"}
        tool = DocumentsUploadTool()
        parameters = {
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "content": "base64encodedcontent",
        }
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"
        assert result.data["filename"] == "test.pdf"


class TestSearchTool:
    """Tests for search tool wrapper."""

    def test_search_global_metadata(self):
        tool = SearchGlobalTool()
        assert tool.tool_name == "search_global"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True
        assert tool.auth_required is False

    @patch("app.services.search.search_all")
    def test_search_global_execute(self, mock_search):
        mock_search.return_value = {"results": [], "total": 0}
        tool = SearchGlobalTool()
        parameters = {"query": "test"}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert "results" in result.data


class TestDashboardTool:
    """Tests for dashboard tool wrapper."""

    def test_dashboard_get_stats_metadata(self):
        tool = DashboardGetStatsTool()
        assert tool.tool_name == "dashboard_get_stats"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True
        assert tool.auth_required is False

    @patch("app.services.dashboard.get_dashboard")
    def test_dashboard_get_stats_execute(self, mock_dashboard):
        mock_dashboard.return_value = {"shipments": {"total": 10}, "invoices": {"total": 5}}
        tool = DashboardGetStatsTool()
        parameters = {}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert "shipments" in result.data


class TestNotificationTool:
    """Tests for notification tool wrapper."""

    def test_notifications_send_metadata(self):
        tool = NotificationsSendTool()
        assert tool.tool_name == "notifications_send"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.NOTIFY
        assert tool.idempotent is False
        assert tool.auth_required is True

    @patch("app.services.notification.send_email")
    def test_notifications_send_execute_email(self, mock_send_email):
        mock_send_email.return_value = {"status": "sent"}
        tool = NotificationsSendTool()
        parameters = {"recipient": "test@example.com", "subject": "Test", "body": "Body"}
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"

    @patch("app.services.notification.send_template_email")
    def test_notifications_send_execute_template(self, mock_send_template_email):
        mock_send_template_email.return_value = {"status": "sent"}
        tool = NotificationsSendTool()
        parameters = {
            "recipient": "test@example.com",
            "subject": "Test",
            "body": "Body",
            "template_id": 1,
        }
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"


class TestWorkflowTools:
    """Tests for workflow tool wrappers."""

    def test_workflow_get_state_metadata(self):
        tool = WorkflowGetStateTool()
        assert tool.tool_name == "workflow_get_state"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.READ
        assert tool.idempotent is True
        assert tool.auth_required is True

    @patch("app.services.workflow.get_workflow")
    def test_workflow_get_state_execute(self, mock_get_workflow):
        mock_get_workflow.return_value = {"workflow_id": 1, "state": "draft"}
        tool = WorkflowGetStateTool()
        parameters = {"workflow_id": 1}
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "success"
        assert result.data["state"] == "draft"

    def test_workflow_transition_metadata(self):
        tool = WorkflowTransitionTool()
        assert tool.tool_name == "workflow_transition"
        assert tool.version == "1.0.0"
        assert tool.side_effects == ToolSideEffect.WRITE
        assert tool.idempotent is False
        assert tool.auth_required is True

    @patch("app.services.workflow.transition_workflow")
    def test_workflow_transition_execute(self, mock_transition):
        mock_transition.return_value = {"workflow_id": 1, "state": "shipped"}
        tool = WorkflowTransitionTool()
        parameters = {"workflow_id": 1, "new_state": "shipped"}
        result = asyncio.run(tool.execute({"user": {"id": 1}}, parameters))
        assert result.status == "success"
        assert result.data["state"] == "shipped"


class TestERPToolErrorHandling:
    """Tests for error handling in ERP tools."""

    @patch("app.services.shipping.fetch_rates")
    def test_tool_returns_error_on_exception(self, mock_fetch_rates):
        mock_fetch_rates.side_effect = Exception("Service error")
        tool = ShippingGetRatesTool()
        parameters = {
            "origin": "EG Cairo",
            "destination": "DE Berlin",
            "weight": 1.0,
        }
        result = asyncio.run(tool.execute({}, parameters))
        assert result.status == "error"
        assert "error" in result.error.lower() or "Service error" in result.error


class TestERPToolMetadataCompliance:
    """Verify all ERP tools carry required metadata fields."""

    def test_all_tools_have_idempotency_key(self):
        tools = [
            ShippingGetRatesTool(),
            ShippingCreateShipmentTool(),
            ShippingPrintLabelTool(),
            EtaSubmitInvoiceTool(),
            EtaCheckStatusTool(),
            CustomsGetDeclarationsTool(),
            CustomsFileDeclarationTool(),
            DocumentsGenerateTool(),
            DocumentsUploadTool(),
            SearchGlobalTool(),
            DashboardGetStatsTool(),
            NotificationsSendTool(),
            WorkflowGetStateTool(),
            WorkflowTransitionTool(),
        ]
        for tool in tools:
            assert tool.idempotency_key is not None, f"{tool.tool_name} missing idempotency_key"
            assert tool.idempotency_key != "", f"{tool.tool_name} has empty idempotency_key"

    def test_all_tools_have_auth_requirements(self):
        tools = [
            ShippingGetRatesTool(),
            ShippingCreateShipmentTool(),
            ShippingPrintLabelTool(),
            EtaSubmitInvoiceTool(),
            EtaCheckStatusTool(),
            CustomsGetDeclarationsTool(),
            CustomsFileDeclarationTool(),
            DocumentsGenerateTool(),
            DocumentsUploadTool(),
            SearchGlobalTool(),
            DashboardGetStatsTool(),
            NotificationsSendTool(),
            WorkflowGetStateTool(),
            WorkflowTransitionTool(),
        ]
        for tool in tools:
            assert tool.auth_requirements is not None, f"{tool.tool_name} missing auth_requirements"
            assert isinstance(tool.auth_requirements, dict), f"{tool.tool_name} auth_requirements not a dict"
            assert "type" in tool.auth_requirements, f"{tool.tool_name} auth_requirements missing type"

    @patch("app.services.shipping.fetch_rates")
    def test_tool_generates_audit_ref_on_success(self, mock_fetch_rates):
        mock_fetch_rates.return_value = [{"carrier": "DHL", "cost": 25.0}]
        tool = ShippingGetRatesTool()
        result = asyncio.run(tool.execute({}, {"origin": "EG", "destination": "DE", "weight": 1.0}))
        assert result.status == "success"
        assert result.audit_ref is not None
        assert result.audit_ref != ""
        assert tool.tool_name in result.audit_ref

    @patch("app.services.shipping.fetch_rates")
    def test_tool_generates_audit_ref_on_error(self, mock_fetch_rates):
        mock_fetch_rates.side_effect = Exception("Service error")
        tool = ShippingGetRatesTool()
        result = asyncio.run(tool.execute({}, {"origin": "EG", "destination": "DE", "weight": 1.0}))
        assert result.status == "error"
        assert result.audit_ref is not None
        assert result.audit_ref != ""
        assert tool.tool_name in result.audit_ref

