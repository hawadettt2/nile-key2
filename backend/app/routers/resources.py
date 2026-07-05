from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.resource import ResourceCreate, ResourceUpdate, Resource
from app.schemas.common import MessageResponse, IdResponse
from app.services.resource import (
    list_resources as _list_resources,
    search_resources as _search_resources,
    get_resource as _get_resource,
    create_resource as _create_resource,
    update_resource as _update_resource,
    delete_resource as _delete_resource,
)

router = APIRouter(prefix="/api/v1/resources", tags=["Resources"])


@router.get("/", response_model=list[Resource])
def list_resources(
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_resources(
        resource_type=resource_type,
        category=category,
        country=country,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=list[Resource])
def search_resources(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    return _search_resources(q=q)


@router.get("/{resource_id}", response_model=Resource)
def get_resource(resource_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_resource(resource_id=resource_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=IdResponse)
def create_resource(data: ResourceCreate, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff"]))):
    return _create_resource(data=data, current_user=current_user)


@router.put("/{resource_id}", response_model=MessageResponse)
def update_resource(resource_id: int, data: ResourceUpdate, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff"]))):
    try:
        return _update_resource(resource_id=resource_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Resource not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.delete("/{resource_id}", response_model=MessageResponse)
def delete_resource(resource_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        return _delete_resource(resource_id=resource_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Resource not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise
