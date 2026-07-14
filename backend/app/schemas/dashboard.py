from pydantic import BaseModel
from typing import Optional


class DashboardStats(BaseModel):
    customers: int = 0
    suppliers: int = 0
    shipments: int = 0
    invoices: int = 0
    customs_declarations: int = 0
    documents: int = 0
    resources: int = 0
    eta_connectors: int = 0


class DashboardTimeline(BaseModel):
    recent_activities: list[dict] = []
    upcoming_shipments: list[dict] = []
    pending_invoices: list[dict] = []


class DashboardResponse(BaseModel):
    stats: DashboardStats
    timeline: DashboardTimeline
    notifications_count: int = 0

    class Config:
        from_attributes = True
