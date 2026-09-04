from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.services.workflow import (
    create_workflow as business_create_workflow,
    get_workflow as business_get_workflow,
    transition_workflow as business_transition_workflow,
    add_workflow_item as business_add_workflow_item,
    _validate_transition,
)
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate


class WorkflowOrchestrator:
    """Coordinates Agent missions with Business Workflows.

    This is a coordination layer, not a new source of truth.
    Business entities (shipments, invoices, customs, documents) remain the source of truth.
    """

    # Mapping from mission types to workflow stages
    MISSION_TYPE_TO_STAGE = {
        "CREATE_SHIPMENT": "shipped",
        "SUBMIT_INVOICE": "customs_ready",
        "FILE_CUSTOMS": "customs_ready",
        "GENERATE_DOCUMENT": "draft",
        "TRANSITION_WORKFLOW": None,  # explicit transition request
    }

    # Mapping from mission result status to workflow transition
    MISSION_STATUS_TO_WORKFLOW = {
        "completed": "advance",
        "failed": "blocked",
        "pending_approval": "paused",
    }

    def __init__(self, db_session_factory, current_user: Optional[dict] = None):
        self.db_session_factory = db_session_factory
        self.current_user = current_user or {}

    async def ensure_workflow_for_mission(
        self,
        session_id: str,
        mission_type: str,
        payload: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create or link a business workflow for the given mission context.

        Returns workflow info dict or None if no workflow is applicable.
        """
        workflow_info = self._extract_workflow_context(payload)
        if not workflow_info:
            return None

        # Check if session already has a workflow
        context = self._get_session_context(session_id)
        existing_workflow_id = context.get("workflow_id") if context else None

        if existing_workflow_id:
            workflow = self._safe_get_workflow(existing_workflow_id)
            if workflow:
                return {**workflow, "linked": True}

        # Create new workflow
        workflow = self._create_workflow(workflow_info, user_id)
        if workflow:
            self._update_session_context(session_id, {"workflow_id": workflow["id"]})
            # Add workflow items for linked entities
            await self._link_entities_to_workflow(workflow["id"], workflow_info)
            return {**workflow, "linked": False}

        return None

    async def update_workflow_state(
        self,
        session_id: str,
        mission_type: str,
        mission_status: str,
        mission_result: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update workflow state based on mission outcome.

        This is called after mission execution to advance/block/pause the workflow.
        """
        context = self._get_session_context(session_id)
        workflow_id = context.get("workflow_id") if context else None
        if not workflow_id:
            return None

        workflow = self._safe_get_workflow(workflow_id)
        if not workflow:
            return None

        current_state = workflow.get("state", "draft")
        action = self.MISSION_STATUS_TO_WORKFLOW.get(mission_status)

        if not action:
            return workflow

        if action == "advance":
            await self._advance_workflow(workflow, mission_type, mission_result, user_id)
        elif action == "blocked":
            await self._block_workflow(workflow, mission_type, mission_result, user_id)
        elif action == "paused":
            # Workflow paused for approval - do not transition
            pass

        return self._safe_get_workflow(workflow_id)

    async def get_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current workflow state for a session."""
        context = self._get_session_context(session_id)
        workflow_id = context.get("workflow_id") if context else None
        if not workflow_id:
            return None
        return self._safe_get_workflow(workflow_id)

    def _extract_workflow_context(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract business entity IDs from mission payload to link to workflow."""
        customer_id = payload.get("customer_id")
        supplier_id = payload.get("supplier_id")

        if not customer_id or not supplier_id:
            return None

        return {
            "customer_id": int(customer_id),
            "supplier_id": int(supplier_id),
            "invoice_id": payload.get("invoice_id"),
            "customs_declaration_id": payload.get("customs_declaration_id"),
            "shipment_id": payload.get("shipment_id"),
            "notes": payload.get("notes"),
        }

    def _get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self.db_session_factory() as db:
                row = db.execute(
                    "SELECT context FROM agent_sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()
                if not row:
                    return None
                import json
                return json.loads(row[0]) if row[0] else {}
        except Exception:
            return None

    def _update_session_context(self, session_id: str, updates: Dict[str, Any]) -> bool:
        try:
            context = self._get_session_context(session_id)
            if context is None:
                return False
            context.update(updates)
            context["updated_at"] = datetime.now(timezone.utc).isoformat()
            import json
            with self.db_session_factory() as db:
                db.execute(
                    "UPDATE agent_sessions SET context = ? WHERE id = ?",
                    (json.dumps(context, default=str), session_id),
                )
                db.commit()
            return True
        except Exception:
            return False

    def _safe_get_workflow(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        try:
            return business_get_workflow(workflow_id)
        except Exception:
            return None

    def _create_workflow(self, workflow_info: Dict[str, Any], user_id: Optional[int]) -> Optional[Dict[str, Any]]:
        try:
            from app.schemas.workflow import ExportWorkflowCreate
            from app.services.workflow import create_workflow
            data = ExportWorkflowCreate(**workflow_info)
            result = create_workflow(data=data, current_user=self.current_user)
            return business_get_workflow(result["id"])
        except Exception:
            return None

    async def _link_entities_to_workflow(self, workflow_id: int, workflow_info: Dict[str, Any]) -> None:
        """Link business entities to workflow as items."""
        try:
            entity_mappings = [
                ("invoice", workflow_info.get("invoice_id")),
                ("customs_declaration", workflow_info.get("customs_declaration_id")),
                ("shipment", workflow_info.get("shipment_id")),
            ]
            for entity_type, entity_id in entity_mappings:
                if entity_id:
                    business_add_workflow_item(
                        workflow_id=workflow_id,
                        data={"workflow_id": workflow_id, "entity_type": entity_type, "entity_id": int(entity_id)},
                        current_user=self.current_user,
                    )
        except Exception:
            pass

    async def _advance_workflow(
        self,
        workflow: Dict[str, Any],
        mission_type: str,
        mission_result: Optional[Dict[str, Any]],
        user_id: Optional[int],
    ) -> None:
        """Advance workflow to the next allowed stage based on mission outcome."""
        current_state = workflow.get("state", "draft")
        target_stage = self.MISSION_TYPE_TO_STAGE.get(mission_type)

        if not target_stage:
            # Use default transition logic from existing workflow service
            target_stage = self._determine_next_stage(current_state, workflow)

        if target_stage and target_stage != current_state:
            try:
                _validate_transition(current_state, target_stage)
                # Check preconditions
                if not self._check_transition_preconditions(target_stage, workflow):
                    return
                business_transition_workflow(
                    workflow_id=workflow["id"],
                    new_state=target_stage,
                    current_user=self.current_user,
                )
            except Exception:
                pass

    async def _block_workflow(
        self,
        workflow: Dict[str, Any],
        mission_type: str,
        mission_result: Optional[Dict[str, Any]],
        user_id: Optional[int],
    ) -> None:
        """Block workflow progression due to mission failure."""
        # Workflow stays in current state but records the block
        try:
            log_audit(
                current_user=self.current_user,
                data=AuditLogCreate(
                    action="workflow_blocked",
                    entity_type="export_workflow",
                    entity_id=workflow["id"],
                    details=f"Blocked by failed mission: {mission_type}",
                ),
            )
        except Exception:
            pass

    def _determine_next_stage(self, current_state: str, workflow: Dict[str, Any]) -> Optional[str]:
        """Determine the next stage based on current state and linked entities."""
        if current_state == "draft":
            if workflow.get("invoice_id") or workflow.get("customs_declaration_id"):
                return "customs_ready"
            if workflow.get("shipment_id"):
                return "shipped"
        elif current_state == "customs_ready":
            if workflow.get("shipment_id"):
                return "shipped"
        elif current_state == "shipped":
            return "delivered"
        return None

    def _check_transition_preconditions(self, target_stage: str, workflow: Dict[str, Any]) -> bool:
        """Check if the workflow has the required entities for the target stage."""
        if target_stage == "customs_ready":
            return bool(workflow.get("customs_declaration_id") or workflow.get("invoice_id"))
        if target_stage == "shipped":
            return bool(workflow.get("shipment_id"))
        if target_stage == "delivered":
            return True
        return True
