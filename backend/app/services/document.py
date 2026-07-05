from typing import Optional

from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.base import connection, parse_json, now_iso, execute_update


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
        "metadata": parse_json(row.get("metadata")),
        "file_name": row.get("file_name"),
        "file_path": row.get("file_path"),
        "file_type": row.get("file_type"),
        "file_size": row.get("file_size"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "created_by": row.get("created_by"),
    }


def list_documents(
    document_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    with connection() as conn:
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
        return [_document_row_to_response(dict(r)) for r in rows]


def get_document(document_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Document not found")
        return _document_row_to_response(dict(row))


def create_document(data: DocumentCreate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        cursor.execute(
            """INSERT INTO documents (title, type, template_type, entity_type, entity_id,
               description, metadata, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.title, data.document_type or "uploaded", data.template_type, data.entity_type,
             data.entity_id, data.content, str(data.metadata) if data.metadata else "{}", now, current_user["id"])
        )
        conn.commit()
        doc_id = cursor.lastrowid
        return {"id": doc_id, "message": "Document created successfully"}


def upload_document(
    title: Optional[str],
    filename: str,
    content_type: str,
    content: bytes,
    entity_type: Optional[str],
    entity_id: Optional[int],
    current_user: dict,
) -> dict:
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if content_type not in allowed_types:
        raise ValueError("Only PDF, JPG, PNG files allowed (max 10MB)")
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("File too large (max 10MB)")
    now = now_iso()
    stored_filename = f"{now}_{filename}"
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO documents (title, type, file_name, file_type, file_size, document_type,
               entity_type, entity_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title or filename, "uploaded", stored_filename, content_type, len(content), "uploaded",
             entity_type, entity_id, now, current_user["id"])
        )
        conn.commit()
        doc_id = cursor.lastrowid
        return {"id": doc_id, "filename": stored_filename, "message": "File uploaded successfully"}


def update_document(document_id: int, data: DocumentUpdate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
        if not cursor.fetchone():
            raise ValueError("Document not found")
        if not execute_update(
            conn=conn,
            table_name="documents",
            record_id=document_id,
            data=data,
            coerce_fields={"metadata": lambda v: str(v) if isinstance(v, dict) else v},
        ):
            return {"message": "No changes"}
        return {"message": "Document updated successfully"}


def delete_document(document_id: int, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
        return {"message": "Document deleted successfully"}
