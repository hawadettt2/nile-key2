from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer, ImportResponse
from app.schemas.common import MessageResponse, IdResponse
from app.services.customer import (
    list_customers as _list_customers,
    get_customer as _get_customer,
    create_customer as _create_customer,
    update_customer as _update_customer,
    delete_customer as _delete_customer,
    import_customers as _import_customers,
)

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get("/", response_model=list[Customer])
def list_customers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_customers(
        search=search,
        status=status,
        country=country,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_customer(customer_id=customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=IdResponse)
def create_customer(data: CustomerCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    return _create_customer(data=data, current_user=current_user)


@router.put("/{customer_id}", response_model=MessageResponse)
def update_customer(customer_id: int, data: CustomerUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    try:
        return _update_customer(customer_id=customer_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Customer not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.delete("/{customer_id}", response_model=MessageResponse)
def delete_customer(customer_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        return _delete_customer(customer_id=customer_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Customer not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/import", response_model=ImportResponse)
def import_customers(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    return _import_customers(file=file.file, filename=file.filename, current_user=current_user)
