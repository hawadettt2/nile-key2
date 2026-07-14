from fastapi import APIRouter, Depends

from app.routers.auth import get_current_user
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard

router = APIRouter(tags=["Dashboard"])


@router.get("/api/v1/dashboard", response_model=DashboardResponse)
def get_dashboard_route(current_user: dict = Depends(get_current_user)):
    return get_dashboard()
