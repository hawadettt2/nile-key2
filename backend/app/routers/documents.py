from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.document import DocumentCreate, DocumentUpdate, Document, DocumentUploadResponse
from app.schemas.common import MessageResponse, IdResponse
from app.services.document import (
    list_documents as _list_documents,
    get_document as _get_document,
    create_document as _create_document,
    upload_document as _upload_document,
    update_document as _update_document,
    delete_document as _delete_document,
)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.get("/", response_model=list[Document])
def list_documents(
    document_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_documents(
        document_type=document_type,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{document_id}", response_model=Document)
def get_document(document_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_document(document_id=document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=IdResponse)
def create_document(data: DocumentCreate, current_user: dict = Depends(get_current_user)):
    return _create_document(data=data, current_user=current_user)


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    content = file.file.read()
    return _upload_document(
        title=title,
        filename=file.filename,
        content_type=file.content_type,
        content=content,
        entity_type=entity_type,
        entity_id=entity_id,
        current_user=current_user,
    )


@router.put("/{document_id}", response_model=MessageResponse)
def update_document(document_id: int, data: DocumentUpdate, current_user: dict = Depends(get_current_user)):
    try:
        return _update_document(document_id=document_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Document not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(document_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    return _delete_document(document_id=document_id, current_user=current_user)
