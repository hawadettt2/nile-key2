from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    Customer,
    CustomerDetail,
    ImportResponse,
    ImportPreviewResponse,
    ImportReviewRequest,
    ImportReviewResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportCleanupResponse,
    CustomerProductResponse,
    CustomerEvidenceResponse,
    CustomerSourceBatchResponse,
)
from app.schemas.common import MessageResponse, IdResponse
from app.services.customer import (
    list_customers as _list_customers,
    get_customer as _get_customer,
    create_customer as _create_customer,
    update_customer as _update_customer,
    delete_customer as _delete_customer,
    import_customers as _import_customers,
    import_preview as _import_preview,
    import_review as _import_review,
    import_confirm as _import_confirm,
    import_cancel as _import_cancel,
    import_cleanup as _import_cleanup,
    get_countries as _get_countries,
    list_source_batches as _list_source_batches,
    list_products as _list_products,
    create_product as _create_product,
    delete_product as _delete_product,
    list_evidence as _list_evidence,
    create_evidence as _create_evidence,
)

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get("/check-source")
def check_customer_source(
    file_id: Optional[str] = Query(default=None),
    sheet_name: Optional[str] = Query(default=None),
    row_number: Optional[int] = Query(default=None),
    country: Optional[str] = Query(default=None),
    company_name: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    from app.services.customer import get_db
    conn = get_db()
    try:
        cursor = conn.cursor()

        if file_id and sheet_name and row_number:
            cursor.execute(
                """
                SELECT cr.id
                FROM customer_raw_records cr
                JOIN customer_source_batches sb ON cr.batch_id = sb.id
                WHERE sb.source_reference = ?
                  AND cr.sheet_name = ?
                  AND cr.row_number = ?
                LIMIT 1
                """,
                (file_id, sheet_name, row_number),
            )
            if cursor.fetchone():
                return {"exists": True}

        if company_name:
            cursor.execute(
                """
                SELECT id
                FROM customers
                WHERE (
                    LOWER(TRIM(name)) = LOWER(TRIM(?))
                    OR LOWER(TRIM(name_en)) = LOWER(TRIM(?))
                )
                LIMIT 1
                """,
                (company_name, company_name),
            )
            if cursor.fetchone():
                return {"exists": True}

        return {"exists": False}
    except Exception:
        return {"exists": False}
    finally:
        conn.close()


@router.get("/", response_model=list[Customer])
def list_customers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    data_status: Optional[str] = None,
    verification_status: Optional[str] = None,
    crm_status: Optional[str] = None,
    activity_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_customers(
        search=search,
        status=status,
        country=country,
        category=category,
        data_status=data_status,
        verification_status=verification_status,
        crm_status=crm_status,
        activity_status=activity_status,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/countries", response_model=list[str])
def get_countries(current_user: dict = Depends(get_current_user)):
    return _get_countries()


@router.get("/source-batches", response_model=list[CustomerSourceBatchResponse])
def list_source_batches(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_source_batches(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_customer(customer_id=customer_id, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
@router.get("/{customer_id}/products", response_model=list[CustomerProductResponse])
def list_products(customer_id: int, current_user: dict = Depends(get_current_user)):
    return _list_products(customer_id=customer_id)


@router.post("/{customer_id}/products", response_model=IdResponse)
def create_product(customer_id: int, data: dict, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    return _create_product(customer_id=customer_id, data=data, current_user=current_user)


@router.delete("/{customer_id}/products/{product_id}", response_model=MessageResponse)
def delete_product(customer_id: int, product_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    return _delete_product(customer_id=customer_id, product_id=product_id, current_user=current_user)


@router.get("/{customer_id}/evidence", response_model=list[CustomerEvidenceResponse])
def list_evidence(customer_id: int, current_user: dict = Depends(get_current_user)):
    return _list_evidence(customer_id=customer_id)


@router.post("/{customer_id}/evidence", response_model=IdResponse)
def create_evidence(customer_id: int, data: dict, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    return _create_evidence(customer_id=customer_id, data=data, current_user=current_user)


@router.post("/", response_model=IdResponse)
def create_customer(data: CustomerCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    try:
        return _create_customer(data=data, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{customer_id}", response_model=MessageResponse)
def update_customer(customer_id: int, data: CustomerUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    try:
        return _update_customer(customer_id=customer_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Customer not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.delete("/{customer_id}", response_model=MessageResponse)
def delete_customer(customer_id: int, current_user: dict = Depends(require_role(["owner"]))):
    try:
        return _delete_customer(customer_id=customer_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Customer not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/import/preview", response_model=ImportPreviewResponse)
def import_preview(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename_required")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail="unsupported_format")
    return _import_preview(file=file.file, filename=file.filename, current_user=current_user)


@router.post("/import/confirm", response_model=ImportConfirmResponse)
def import_confirm(
    request: ImportConfirmRequest,
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    return _import_confirm(request=request, current_user=current_user)


@router.post("/import/review", response_model=ImportReviewResponse)
def import_review(
    request: ImportReviewRequest,
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    return _import_review(request=request, current_user=current_user)


@router.post("/import/cleanup", response_model=ImportCleanupResponse)
def import_cleanup(
    current_user: dict = Depends(require_role(["owner", "manager"]))
):
    return _import_cleanup(current_user=current_user)


@router.post("/import/cancel", response_model=MessageResponse)
def import_cancel(
    batch_id: int,
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    return _import_cancel(batch_id=batch_id, current_user=current_user)


@router.post("/import", response_model=ImportResponse)
def import_customers(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    return _import_customers(file=file.file, filename=file.filename, current_user=current_user)
