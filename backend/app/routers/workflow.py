from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.routers.auth import require_role
from app.schemas.workflow import (
    ExportWorkflow,
    ExportWorkflowCreate,
    ExportWorkflowUpdate,
    ExportWorkflowItemCreate,
    ExportWorkflowSummary,
    ExportWorkflowListResponse,
)
from app.schemas.common import MessageResponse
from app.services.workflow import (
    list_workflows,
    count_workflows,
    get_workflow,
    create_workflow,
    update_workflow,
    submit_workflow,
    generate_workflow_summary,
    add_workflow_item,
)

router = APIRouter(tags=["Export Workflow"])


@router.get("/api/v1/export-workflows", response_model=ExportWorkflowListResponse)
def list_export_workflows(
    state: Optional[str] = Query(None, description="Filter by workflow state"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    current_user: dict = Depends(require_role(["owner", "manager", "admin_staff", "logistics"])),
):
    try:
        items = list_workflows(
            state=state,
            customer_id=customer_id,
            supplier_id=supplier_id,
            skip=skip,
            limit=limit,
        )
        total = count_workflows(
            state=state,
            customer_id=customer_id,
            supplier_id=supplier_id,
        )
        return ExportWorkflowListResponse(total=total, skip=skip, limit=limit, items=items)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch export workflows")


@router.post("/api/v1/export-workflows", response_model=dict)
def create_export_workflow(data: ExportWorkflowCreate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        return create_workflow(data=data, current_user=current_user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to create export workflow")


@router.get("/api/v1/export-workflows/{workflow_id}", response_model=dict)
def get_export_workflow(workflow_id: int, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff", "logistics"]))):
    try:
        return get_workflow(workflow_id=workflow_id)
    except ValueError as exc:
        if str(exc) == "Workflow not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.put("/api/v1/export-workflows/{workflow_id}", response_model=MessageResponse)
def update_export_workflow(workflow_id: int, data: ExportWorkflowUpdate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        return update_workflow(workflow_id=workflow_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Workflow not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/api/v1/export-workflows/{workflow_id}/submit", response_model=dict)
def submit_export_workflow(workflow_id: int, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        return submit_workflow(workflow_id=workflow_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Workflow not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.get("/api/v1/export-workflows/{workflow_id}/summary", response_model=ExportWorkflowSummary)
def get_export_workflow_summary(workflow_id: int, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff", "logistics"]))):
    try:
        return generate_workflow_summary(workflow_id=workflow_id)
    except ValueError as exc:
        if str(exc) == "Workflow not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/api/v1/export-workflows/{workflow_id}/items", response_model=dict)
def add_export_workflow_item(workflow_id: int, data: ExportWorkflowItemCreate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        data.workflow_id = workflow_id
        return add_workflow_item(data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Workflow not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise
