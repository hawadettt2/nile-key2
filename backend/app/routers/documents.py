from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from datetime import datetime
from typing import Optional
import json

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.document import DocumentCreate, DocumentUpdate, Document, DocumentUploadResponse
from app.schemas.common import MessageResponse, IdResponse

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


def _document_row_to_response(row: dict) -> dict:
    """Compatibility layer: map DB row to API contract fields.
    
    LEGACY COMPATIBILITY:
    - Returns only backend contract fields
    - Legacy column `type` maps to `document_type`
    - Deferred cleanup to WP-10
    """
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "document_type": row.get("document_type") or row.get("type"),
        "template_type": row.get("template_type"),
        "entity_type": row.get("entity_type"),
        "entity_id": row.get("entity_id"),
        "content": row.get("description"),
        "metadata": json.loads(row.get("metadata")) if row.get("metadata") else {},
        "file_name": row.get("file_name"),
        "file_path": row.get("file_path"),
        "file_type": row.get("file_type"),
        "file_size": row.get("file_size"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "created_by": row.get("created_by"),
    }


@router.get("/", response_model=list[Document])
def list_documents(
    document_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM documents WHERE 1=1"
    params = []
    if document_type:
        query += " AND (document_type = ? OR type = ?)"
        params.extend([document_type, document_type])
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_document_row_to_response(dict(r)) for r in rows]


@router.get("/{document_id}", response_model=Document)
def get_document(document_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return _document_row_to_response(dict(row))


@router.post("/", response_model=IdResponse)
def create_document(data: DocumentCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO documents (title, type, template_type, entity_type, entity_id,
           description, metadata, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.title, data.document_type or "uploaded", data.template_type, data.entity_type,
         data.entity_id, data.content, str(data.metadata) if data.metadata else "{}", now, current_user["id"])
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return {"id": doc_id, "message": "Document created successfully"}


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, PNG files allowed (max 10MB)")
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    now = datetime.utcnow().isoformat()
    filename = f"{now}_{file.filename}"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO documents (title, file_name, file_type, file_size, document_type,
           entity_type, entity_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (title or file.filename, filename, file.content_type, len(content), "uploaded",
         entity_type, entity_id, now, current_user["id"])
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return {"id": doc_id, "filename": filename, "message": "File uploaded successfully"}


@router.put("/{document_id}", response_model=MessageResponse)
def update_document(document_id: int, data: DocumentUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    if not execute_update(
        conn=conn,
        table_name="documents",
        record_id=document_id,
        data=data,
        coerce_fields={"metadata": lambda v: str(v) if isinstance(v, dict) else v},
    ):
        return {"message": "No changes"}
    return {"message": "Document updated successfully"}


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(document_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    return {"message": "Document deleted successfully"}
