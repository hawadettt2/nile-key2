from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional
import random

from app.core.database import get_db
from app.routers.auth import get_current_user, require_role
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShippingRateRequest, ShippingRate

router = APIRouter(prefix="/api/v1/shipping", tags=["Shipping"])

CARRIERS = {
    "DHL": {"services": ["Express", "Economy"], "base_rate": 25.0},
    "FedEx": {"services": ["International Priority", "International Economy"], "base_rate": 28.0},
    "Aramex": {"services": ["Express", "Ground"], "base_rate": 20.0},
    "LetMeShip": {"services": ["Standard", "Premium"], "base_rate": 22.0},
    "SendCloud": {"services": ["Standard", "Express"], "base_rate": 18.0},
}


@router.get("/rates", response_model=list)
def get_rates(request: ShippingRateRequest, current_user: dict = Depends(get_current_user)):
    rates = []
    for carrier, info in CARRIERS.items():
        for service in info["services"]:
            weight_factor = max(1, request.weight * 0.5)
            distance_factor = random.uniform(0.8, 1.5)
            cost = round(info["base_rate"] * weight_factor * distance_factor, 2)
            days = random.randint(2, 10)
            rates.append(ShippingRate(
                carrier=carrier,
                service=service,
                estimated_days=days,
                cost=cost,
                currency="USD"
            ))
    return sorted(rates, key=lambda x: x.cost)


@router.get("/shipments", response_model=list)
def list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM shipments WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/track/{tracking_id}", response_model=dict)
def track_shipment(tracking_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE tracking_number = ? OR id = ?", (tracking_id, tracking_id))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment = dict(row)
    shipment["tracking_events"] = [
        {"status": "picked_up", "location": shipment.get("origin", ""), "timestamp": shipment.get("shipped_at")},
        {"status": "in_transit", "location": "Transit Hub", "timestamp": None},
        {"status": shipment.get("status", "pending"), "location": shipment.get("destination", ""), "timestamp": shipment.get("delivered_at")},
    ]
    return shipment


@router.get("/shipments/{shipment_id}", response_model=dict)
def get_shipment(shipment_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return dict(row)


@router.post("/shipments", response_model=dict)
def create_shipment(data: ShipmentCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales", "logistics"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    tracking = f"NK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
    cursor.execute(
        """INSERT INTO shipments (tracking_number, reference, supplier_id, customer_id, origin, destination,
           carrier, service_type, status, weight, weight_unit, dimensions, value, currency, items_count,
           description, eta, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tracking, data.reference, data.supplier_id, data.customer_id, data.origin, data.destination,
         data.carrier, data.service_type, "pending", data.weight, data.weight_unit, data.dimensions,
         data.value, data.currency, data.items_count, data.description,
         data.eta.isoformat() if data.eta else None, now, current_user["id"])
    )
    conn.commit()
    shipment_id = cursor.lastrowid
    conn.close()
    return {"id": shipment_id, "tracking_number": tracking, "message": "Shipment created successfully"}


@router.put("/shipments/{shipment_id}", response_model=dict)
def update_shipment(shipment_id: int, data: ShipmentUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales", "logistics"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM shipments WHERE id = ?", (shipment_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Shipment not found")
    fields = []
    values = []
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            fields.append(f"{field} = ?")
            if hasattr(value, 'isoformat'):
                values.append(value.isoformat())
            else:
                values.append(value)
    if not fields:
        conn.close()
        return {"message": "No changes"}
    values.append(shipment_id)
    cursor.execute(f"UPDATE shipments SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
                   (*values, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Shipment updated successfully"}


@router.get("/shipments/{shipment_id}/label", response_model=dict)
def get_label(shipment_id: int, current_user: dict = Depends(get_current_user)):
    return {"shipment_id": shipment_id, "label_url": f"/api/v1/shipping/shipments/{shipment_id}/label.pdf", "message": "Label generated"}
