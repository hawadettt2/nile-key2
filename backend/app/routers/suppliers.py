from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.supplier import SupplierCreate, SupplierUpdate, Supplier
from app.schemas.common import MessageResponse, IdResponse
from app.services.supplier import (
    list_suppliers as _list_suppliers,
    get_supplier as _get_supplier,
    create_supplier as _create_supplier,
    update_supplier as _update_supplier,
    delete_supplier as _delete_supplier,
)

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers"])


@router.get("/", response_model=list[Supplier])
def list_suppliers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_suppliers(
        search=search,
        status=status,
        city=city,
        skip=skip,
        limit=limit,
    )


@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_supplier(supplier_id=supplier_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=IdResponse)
def create_supplier(data: SupplierCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    return _create_supplier(data=data, current_user=current_user)


@router.put("/{supplier_id}", response_model=MessageResponse)
def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    try:
        return _update_supplier(supplier_id=supplier_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Supplier not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.delete("/{supplier_id}", response_model=MessageResponse)
def delete_supplier(supplier_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        return _delete_supplier(supplier_id=supplier_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Supplier not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise
