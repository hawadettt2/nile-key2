from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user
from app.schemas.common import MessageResponse
from app.services.export_readiness import ExportReadinessService, ExportReadinessRequest

router = APIRouter(prefix="/api/v1/export-readiness", tags=["Export Readiness"])


def _raise_http_error(result: dict) -> None:
    if not isinstance(result, dict):
        return
    error_code = result.get("error_code")
    if not error_code:
        return
    category = result.get("category", "internal")
    status_map = {
        "not_found": 404,
        "validation": 422,
        "dependency": 503,
        "internal": 500,
        "permission": 403,
    }
    status_code = status_map.get(category, 400)
    raise HTTPException(status_code=status_code, detail=result)


@router.post("/analyze", response_model=dict)
async def analyze_export_readiness(
    request: ExportReadinessRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        user_id = current_user["id"]
    except (KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user context")

    service = ExportReadinessService()
    try:
        report = await service.analyze(request=request, user_id=user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export readiness analysis failed: {exc}") from exc

    return report.model_dump(mode="json")
