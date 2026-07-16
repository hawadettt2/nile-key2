import uuid
from typing import Any, Dict, Optional
from datetime import datetime

from .base import BaseTool, ToolResult, ToolSideEffect


# ========== Shipping Tools ==========

class ShippingGetRatesTool(BaseTool):
    tool_name = "shipping_get_rates"
    description = "Get available shipping rates from providers"
    input_schema = {
        "origin": {"type": "string", "required": True},
        "destination": {"type": "string", "required": True},
        "weight": {"type": "number", "required": True},
        "weight_unit": {"type": "string", "required": False},
        "parcels": {"type": "array", "required": False},
    }
    output_schema = {"rates": {"type": "array"}, "carrier": {"type": "string"}, "cost": {"type": "number"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "shipping_get_rates"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.shipping import fetch_rates
            from app.schemas.shipping import RateRequest, Parcel

            parcels = None
            if "parcels" in parameters:
                parcels = [Parcel(**p) for p in parameters["parcels"]]

            rate_request = RateRequest(
                origin=parameters.get("origin", ""),
                destination=parameters.get("destination", ""),
                weight=float(parameters.get("weight", 0)),
                weight_unit=parameters.get("weight_unit", "kg"),
                parcels=parcels,
            )
            rates = fetch_rates(rate_request)
            return ToolResult(status="success", data={"rates": rates}, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class ShippingCreateShipmentTool(BaseTool):
    tool_name = "shipping_create_shipment"
    description = "Create a new shipment"
    input_schema = {
        "provider": {"type": "string", "required": True},
        "service": {"type": "string", "required": True},
        "origin": {"type": "string", "required": True},
        "destination": {"type": "string", "required": True},
        "weight": {"type": "number", "required": True},
        "parcels": {"type": "array", "required": False},
        "pickup_address": {"type": "object", "required": False},
        "delivery_address": {"type": "object", "required": False},
        "pickup_contact": {"type": "object", "required": False},
        "delivery_contact": {"type": "object", "required": False},
    }
    output_schema = {"shipment_id": {"type": "integer"}, "tracking_number": {"type": "string"}, "status": {"type": "string"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "shipping_create_shipment"
    auth_requirements = {"type": "role_based", "roles": ["owner", "manager", "sales", "logistics"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.shipping import create_shipment
            from app.schemas.shipping import CreateShipmentRequest, ShippingAddress, ShippingContact, Parcel

            parcels = None
            if "parcels" in parameters:
                parcels = [Parcel(**p) for p in parameters["parcels"]]
            pickup_address = ShippingAddress(**parameters.get("pickup_address", {})) if parameters.get("pickup_address") else None
            delivery_address = ShippingAddress(**parameters.get("delivery_address", {})) if parameters.get("delivery_address") else None
            pickup_contact = ShippingContact(**parameters.get("pickup_contact", {})) if parameters.get("pickup_contact") else None
            delivery_contact = ShippingContact(**parameters.get("delivery_contact", {})) if parameters.get("delivery_contact") else None

            data = CreateShipmentRequest(
                provider=parameters.get("provider", ""),
                service=parameters.get("service", ""),
                origin=parameters.get("origin", ""),
                destination=parameters.get("destination", ""),
                weight=float(parameters.get("weight", 0)),
                parcels=parcels,
                pickup_address=pickup_address,
                delivery_address=delivery_address,
                pickup_contact=pickup_contact,
                delivery_contact=delivery_contact,
            )
            user = context.get("user", {})
            result = create_shipment(data, user)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class ShippingPrintLabelTool(BaseTool):
    tool_name = "shipping_print_label"
    description = "Print shipping label for a shipment"
    input_schema = {"shipment_id": {"type": "integer", "required": True}}
    output_schema = {"label_url": {"type": "string"}, "shipment_id": {"type": "integer"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "shipping_print_label"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.shipping import get_label

            shipment_id = int(parameters.get("shipment_id", 0))
            label = get_label(shipment_id)
            return ToolResult(status="success", data=label, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== ETA Tools ==========

class EtaSubmitInvoiceTool(BaseTool):
    tool_name = "eta_submit_invoice"
    description = "Submit invoice to ETA"
    input_schema = {"invoice_id": {"type": "integer", "required": True}, "connector_id": {"type": "integer", "required": True}}
    output_schema = {"status": {"type": "string"}, "submission_id": {"type": "string"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "eta_submit_invoice"
    auth_requirements = {"type": "role_based", "roles": ["owner", "accountant"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.eta import submit_invoice_to_eta

            invoice_id = int(parameters.get("invoice_id", 0))
            connector_id = int(parameters.get("connector_id", 0))
            user = context.get("user", {})
            result = submit_invoice_to_eta(invoice_id, connector_id, user)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class EtaCheckStatusTool(BaseTool):
    tool_name = "eta_check_status"
    description = "Check ETA submission status"
    input_schema = {"invoice_id": {"type": "integer", "required": True}}
    output_schema = {"status": {"type": "string"}, "eta_status": {"type": "string"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "eta_check_status"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.eta import get_eta_invoice_status

            invoice_id = int(parameters.get("invoice_id", 0))
            result = get_eta_invoice_status(invoice_id)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Customs Tools ==========

class CustomsGetDeclarationsTool(BaseTool):
    tool_name = "customs_get_declarations"
    description = "Get customs declarations"
    input_schema = {"declaration_id": {"type": "integer", "required": False}, "status": {"type": "string", "required": False}}
    output_schema = {"declarations": {"type": "array"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "customs_get_declarations"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.customs import list_declarations, get_declaration

            declaration_id = parameters.get("declaration_id")
            if declaration_id:
                result = get_declaration(int(declaration_id))
                return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
            else:
                results = list_declarations()
                return ToolResult(status="success", data={"declarations": results}, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class CustomsFileDeclarationTool(BaseTool):
    tool_name = "customs_file_declaration"
    description = "File customs declaration"
    input_schema = {"declaration_id": {"type": "integer", "required": True}}
    output_schema = {"status": {"type": "string"}, "declaration_id": {"type": "integer"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "customs_file_declaration"
    auth_requirements = {"type": "role_based", "roles": ["owner", "manager", "logistics"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.customs import submit_declaration

            declaration_id = int(parameters.get("declaration_id", 0))
            user = context.get("user", {})
            result = submit_declaration(declaration_id, user)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Document Tools ==========

class DocumentsGenerateTool(BaseTool):
    tool_name = "documents_generate"
    description = "Generate a new document"
    input_schema = {"title": {"type": "string", "required": True}, "document_type": {"type": "string", "required": True}, "content": {"type": "string", "required": False}}
    output_schema = {"document_id": {"type": "integer"}, "title": {"type": "string"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "documents_generate"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.document import create_document
            from app.schemas.document import DocumentCreate

            data = DocumentCreate(
                title=parameters.get("title", ""),
                document_type=parameters.get("document_type", ""),
                content=parameters.get("content", ""),
            )
            user = context.get("user", {})
            result = create_document(data, user)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class DocumentsUploadTool(BaseTool):
    tool_name = "documents_upload"
    description = "Upload a document"
    input_schema = {
        "title": {"type": "string", "required": False},
        "filename": {"type": "string", "required": True},
        "content_type": {"type": "string", "required": True},
        "content": {"type": "string", "required": True},
        "entity_type": {"type": "string", "required": False},
        "entity_id": {"type": "integer", "required": False},
    }
    output_schema = {"id": {"type": "integer"}, "filename": {"type": "string"}, "message": {"type": "string"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "documents_upload"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            import base64
            from app.services.document import upload_document

            title = parameters.get("title")
            filename = parameters.get("filename", "")
            content_type = parameters.get("content_type", "application/pdf")
            content_str = parameters.get("content", "")
            entity_type = parameters.get("entity_type")
            entity_id = parameters.get("entity_id")
            user = context.get("user", {})

            if isinstance(content_str, str):
                content = base64.b64decode(content_str)
            else:
                content = content_str

            result = upload_document(
                title=title,
                filename=filename,
                content_type=content_type,
                content=content,
                entity_type=entity_type,
                entity_id=entity_id,
                current_user=user,
            )
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Search Tool ==========

class SearchGlobalTool(BaseTool):
    tool_name = "search_global"
    description = "Search across all entities"
    input_schema = {"query": {"type": "string", "required": True}, "entity_type": {"type": "string", "required": False}}
    output_schema = {"results": {"type": "array"}, "total": {"type": "integer"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = False
    version = "1.0.0"
    idempotency_key = "search_global"
    auth_requirements = {"type": "role_based", "roles": ["owner", "manager", "sales", "admin_staff", "accountant", "logistics"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.search import search_all

            query = parameters.get("query", "")
            entity_type = parameters.get("entity_type")
            result = search_all(query, entity_type)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Dashboard Tool ==========

class DashboardGetStatsTool(BaseTool):
    tool_name = "dashboard_get_stats"
    description = "Get dashboard statistics"
    input_schema = {}
    output_schema = {"shipments": {"type": "object"}, "invoices": {"type": "object"}, "activities": {"type": "array"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = False
    version = "1.0.0"
    idempotency_key = "dashboard_get_stats"
    auth_requirements = {"type": "authenticated"}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.dashboard import get_dashboard

            result = get_dashboard()
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Notification Tool ==========

class NotificationsSendTool(BaseTool):
    tool_name = "notifications_send"
    description = "Send a notification"
    input_schema = {"recipient": {"type": "string", "required": True}, "subject": {"type": "string", "required": True}, "body": {"type": "string", "required": True}, "template_id": {"type": "integer", "required": False}}
    output_schema = {"status": {"type": "string"}, "message_id": {"type": "string"}}
    side_effects = ToolSideEffect.NOTIFY
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "notifications_send"
    auth_requirements = {"type": "role_based", "roles": ["owner", "admin_staff"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.notification import send_email, send_template_email

            template_id = parameters.get("template_id")
            if template_id:
                current_user = context.get("user", {})
                result = send_template_email(
                    template_id=int(template_id),
                    recipient=parameters.get("recipient", ""),
                    variables={
                        "subject": parameters.get("subject", ""),
                        "body": parameters.get("body", ""),
                    },
                    current_user=current_user,
                )
            else:
                result = send_email(
                    to=parameters.get("recipient", ""),
                    subject=parameters.get("subject", ""),
                    body=parameters.get("body", ""),
                )
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


# ========== Workflow Tools ==========

class WorkflowGetStateTool(BaseTool):
    tool_name = "workflow_get_state"
    description = "Get current workflow state"
    input_schema = {"workflow_id": {"type": "integer", "required": True}}
    output_schema = {"workflow_id": {"type": "integer"}, "state": {"type": "string"}, "workflow_number": {"type": "string"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = True
    version = "1.0.0"
    idempotency_key = "workflow_get_state"
    auth_requirements = {"type": "role_based", "roles": ["owner", "manager", "admin_staff", "logistics"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.workflow import get_workflow

            workflow_id = int(parameters.get("workflow_id", 0))
            result = get_workflow(workflow_id)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")


class WorkflowTransitionTool(BaseTool):
    tool_name = "workflow_transition"
    description = "Transition workflow to a new state"
    input_schema = {"workflow_id": {"type": "integer", "required": True}, "new_state": {"type": "string", "required": True}}
    output_schema = {"workflow_id": {"type": "integer"}, "state": {"type": "string"}}
    side_effects = ToolSideEffect.WRITE
    idempotent = False
    auth_required = True
    version = "1.0.0"
    idempotency_key = "workflow_transition"
    auth_requirements = {"type": "role_based", "roles": ["owner", "manager", "logistics"]}

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        try:
            from app.services.workflow import transition_workflow

            workflow_id = int(parameters.get("workflow_id", 0))
            new_state = parameters.get("new_state", "")
            user = context.get("user", {})
            result = transition_workflow(workflow_id, new_state, user)
            return ToolResult(status="success", data=result, audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
        except Exception as e:
            return ToolResult(status="error", error=str(e), audit_ref=f"{self.tool_name}:{uuid.uuid4()}")
