import random
from datetime import datetime
from typing import Optional

from app.core.database import get_db, execute_update
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShippingRateRequest


CARRIERS = {
    "DHL": {"services": ["Express", "Economy"], "base_rate": 25.0},
    "FedEx": {"services": ["International Priority", "International Economy"], "base_rate": 28.0},
    "Aramex": {"services": ["Express", "Ground"], "base_rate": 20.0},
    "LetMeShip": {"services": ["Standard", "Premium"], "base_rate": 22.0},
    "SendCloud": {"services": ["Standard", "Express"], "base_rate": 18.0},
}


def get_rates(request: ShippingRateRequest) -> list[dict]:
    rates = []
    for carrier, info in CARRIERS.items():
        for service in info["services"]:
            weight_factor = max(1, request.weight * 0.5)
            distance_factor = random.uniform(0.8, 1.5)
            cost = round(info["base_rate"] * weight_factor * distance_factor, 2)
            days = random.randint(2, 10)
            rates.append({
                "carrier": carrier,
                "service": service,
                "estimated_days": days,
                "cost": cost,
                "currency": "USD",
            })
    return sorted(rates, key=lambda x: x["cost"])


def list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
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


def track_shipment(tracking_id: str) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE tracking_number = ? OR id = ?", (tracking_id, tracking_id))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError("Shipment not found")
    shipment = dict(row)
    shipment["tracking_events"] = [
        {"status": "picked_up", "location": shipment.get("origin", ""), "timestamp": shipment.get("shipped_at")},
        {"status": "in_transit", "location": "Transit Hub", "timestamp": None},
        {"status": shipment.get("status", "pending"), "location": shipment.get("destination", ""), "timestamp": shipment.get("delivered_at")},
    ]
    return shipment


def get_shipment(shipment_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError("Shipment not found")
    result = dict(row)
    if result.get("origin") is None:
        result["origin"] = ""
    if result.get("destination") is None:
        result["destination"] = ""
    return result


def create_shipment(data, current_user: dict) -> dict:
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


def update_shipment(shipment_id: int, data: ShipmentUpdate, current_user: dict) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM shipments WHERE id = ?", (shipment_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Shipment not found")
    if not execute_update(
        conn=conn,
        table_name="shipments",
        record_id=shipment_id,
        data=data,
        coerce_fields={"eta": lambda v: v.isoformat() if hasattr(v, "isoformat") else v},
    ):
        return {"message": "No changes"}
    conn.close()
    return {"message": "Shipment updated successfully"}


def get_label(shipment_id: int) -> dict:
    return {"shipment_id": shipment_id, "label_url": f"/api/v1/shipping/shipments/{shipment_id}/label.pdf", "message": "Label generated"}
