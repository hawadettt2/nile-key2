"""
Shipping Engine Orchestrator
- Provider registry + lazy initialization from DB + env vars
- Rate aggregation across enabled providers
- Shipment booking, label retrieval, tracking, cancellation
- Provider CRUD, parcel template CRUD
- Audit logging via shipping_logs
- Validation helpers
"""

import json
import os
import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import get_db_connection
from app.core.config import settings
from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential
from app.core.credentials.client_id_secret_credential import ClientIdSecretCredential
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.schemas.shipping import (
    RateRequest, ShippingRate,
    CreateShipmentRequest, ShipmentResult,
    LabelResponse, TrackingEvent, TrackingResponse,
    ShippingProviderCreate, ShippingProviderUpdate, ShippingProviderResponse,
    ParcelTemplateCreate, ParcelTemplateUpdate, ParcelTemplateResponse,
    Parcel, ShippingAddress, ShippingContact,
)
from app.services.shipping.base import (
    ShippingProvider, ShippingError, ProviderNotFoundError,
    ShipmentBookingError, TrackingError, ValidationError,
    register_provider, get_provider, get_enabled_providers, PROVIDERS,
)
from app.services.notification import send_template_email, TemplateNotFoundError, TemplateInactiveError, EmailSendError, _is_notification_enabled

logger = logging.getLogger("shipping")

credential_store = CredentialStore()

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "labels")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _get_user_email(user_id: int) -> Optional[str]:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            try:
                return dict(row).get("email")
            except (TypeError, ValueError):
                return row[0] if row else None
    except Exception:
        return None


def _send_shipping_notification(
    template_id: int,
    user_id: Optional[int],
    variables: Optional[dict] = None,
    current_user: Optional[dict] = None,
) -> None:
    if user_id is None:
        return
    if not _is_notification_enabled(user_id, "shipping"):
        logger.info("Shipping notification skipped for user %s: preference disabled", user_id)
        return
    email = _get_user_email(user_id)
    if not email:
        logger.warning("Shipping notification skipped: no email for user %s", user_id)
        return
    try:
        result = send_template_email(
            template_id=template_id,
            recipient=email,
            variables=variables,
            current_user=current_user,
        )
        if result.get("status") == "failed":
            logger.warning("Shipping notification failed: %s", result.get("error"))
    except (TemplateNotFoundError, TemplateInactiveError) as exc:
        logger.warning("Shipping notification skipped: %s", str(exc))
    except EmailSendError as exc:
        logger.warning("Shipping notification failed: %s", str(exc))


def _build_letmeship_client(provider_row: dict) -> "LetMeShipClient":
    from app.services.shipping.letmeship_client import LetMeShipClient
    return LetMeShipClient(
        api_id=settings.LETME_API_ID,
        api_password=settings.LETME_API_PASSWORD,
        environment=provider_row.get("environment", "Pre-Production"),
        credential_store=credential_store,
    )


def _build_sendcloud_client(provider_row: dict) -> "SendCloudClient":
    from app.services.shipping.sendcloud_client import SendCloudClient
    return SendCloudClient(
        public_key=settings.SENDCLOUD_PUBLIC_KEY,
        secret_key=settings.SENDCLOUD_SECRET_KEY,
        environment=provider_row.get("environment", "Pre-Production"),
        credential_store=credential_store,
    )


def _build_client(provider_row: dict) -> Optional[ShippingProvider]:
    ptype = provider_row.get("provider_type", "").lower()
    if ptype == "letmeship":
        return _build_letmeship_client(provider_row)
    if ptype == "sendcloud":
        return _build_sendcloud_client(provider_row)
    logger.warning("Unknown provider type: %s", ptype)
    return None


def _init_providers():
    if PROVIDERS:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipping_providers WHERE enabled = 1")
        rows = cursor.fetchall()
    for row in rows:
        row_dict = dict(row)
        client = _build_client(row_dict)
        if client:
            register_provider(row_dict["name"], client)


# ========== Validation Helpers ==========

def validate_phone(phone: Optional[str]) -> str:
    if not phone:
        raise ValidationError("Phone is required")
    cleaned = re.sub(r"[^\d+]", "", phone)
    if not re.match(r"^\+[1-9]\d{6,14}$", cleaned):
        raise ValidationError(f"Phone must be E.164 format: {phone}")
    return cleaned


def validate_address(address: ShippingAddress) -> ShippingAddress:
    if not address.country:
        raise ValidationError("Country is required")
    if not address.pincode:
        raise ValidationError("Pincode is required")
    address.pincode = address.pincode.replace(" ", "")
    if address.country_code is None and len(address.country) == 2:
        address.country_code = address.country.upper()
    return address


def validate_parcels(parcels: Optional[List[Parcel]]) -> List[Parcel]:
    if not parcels:
        return []
    for p in parcels:
        if p.length < 1 or p.width < 1 or p.height < 1:
            raise ValidationError("Parcel dimensions must be >= 1")
    return parcels


def _normalize_letmeship_address(address: ShippingAddress) -> dict:
    return {
        "address_title": address.title[:30] if address.title else address.line1[:30],
        "address_line1": address.line1,
        "address_line2": address.line2 or "",
        "city": address.city,
        "postal_code": address.pincode,
        "country": address.country,
        "country_code": address.country_code or address.country[:2].upper(),
    }


def _normalize_letmeship_contact(contact: Optional[ShippingContact]) -> dict:
    if not contact:
        return {}
    title = (contact.title or "MR" if contact.gender == "male" else "MS").upper()
    phone = contact.phone or ""
    prefix = phone[:3] if len(phone) > 3 else ""
    digits = re.sub(r"[^\d]", "", phone[3:]) if len(phone) > 3 else re.sub(r"[^\d]", "", phone)
    return {
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email or "",
        "phone_prefix": prefix,
        "phone_number": digits,
        "title": title,
    }


def _normalize_sendcloud_address(address: ShippingAddress) -> dict:
    line1 = address.line1
    house_number_match = re.search(r"\d+", line1)
    house_number = house_number_match.group(0) if house_number_match else "\u200A"
    street = re.sub(r"\d+", "", line1).strip() if house_number_match else line1
    return {
        "street": street,
        "house_number": house_number,
        "city": address.city,
        "postal_code": address.pincode,
        "country": address.country_code or address.country[:2].upper(),
    }


# ========== Rate Calculation ==========

def fetch_rates(request: RateRequest) -> List[Dict[str, Any]]:
    _init_providers()
    results: List[Dict[str, Any]] = []
    providers = get_enabled_providers()
    if not providers:
        return results

    for provider in providers:
        try:
            rates = provider.get_available_services(request)
            for r in rates:
                results.append({
                    "carrier": r.get("carrier", r.get("name", provider.__class__.__name__)),
                    "service": r.get("service", r.get("name", "")),
                    "service_id": r.get("service_id"),
                    "estimated_days": r.get("estimated_days", r.get("delivery_days", 0)),
                    "cost": float(r.get("cost", r.get("price", 0))),
                    "currency": r.get("currency", "USD"),
                    "is_preferred": r.get("is_preferred", False),
                    "provider": provider.__class__.__name__.replace("Client", "").replace("Provider", ""),
                    "raw": r,
                })
        except Exception as exc:
            logger.error("Rate fetch failed for %s: %s", provider.__class__.__name__, exc)
            _log_shipping(None, provider.__class__.__name__.replace("Client", "").replace("Provider", ""), "rates", str(request.model_dump(exclude_none=True)), None, str(exc), 500)

    results.sort(key=lambda x: x["cost"])
    return results


# ========== Shipment Booking ==========

def create_shipment(data: CreateShipmentRequest, user: dict) -> ShipmentResult:
    _init_providers()
    provider = None
    raw = {}
    try:
        provider = get_provider(data.provider)
    except ProviderNotFoundError:
        logger.warning("Provider '%s' not found, creating local-only shipment", data.provider)

    if provider:
        try:
            validate_parcels(data.parcels)
            if data.pickup_contact:
                validate_phone(data.pickup_contact.phone)
            if data.delivery_contact:
                validate_phone(data.delivery_contact.phone)
            if data.pickup_address:
                validate_address(data.pickup_address)
            if data.delivery_address:
                validate_address(data.delivery_address)
        except ValidationError as exc:
            raise ShipmentBookingError(str(exc))

        ptype = provider.__class__.__name__.lower()
        if "letmeship" in ptype:
            payload = _build_letmeship_create_payload(data)
        else:
            payload = _build_sendcloud_create_payload(data)

        try:
            raw = provider.create_shipment(payload)
        except Exception as exc:
            _log_shipping(None, data.provider, "create", json.dumps(payload), None, str(exc), 500)
            raise ShipmentBookingError(str(exc))

    shipment_id = _insert_shipment(data, user, raw)
    _log_shipping(shipment_id, data.provider, "create", json.dumps(raw), json.dumps(raw), None, 200 if raw else 0)

    result = _parse_create_response(data.provider, raw, shipment_id)
    if raw:
        _insert_shipping_label(shipment_id, data.provider, result.provider_shipment_id, result.label_url)
    log_audit(
        current_user=user,
        data=AuditLogCreate(action="create", entity_type="shipment", entity_id=shipment_id, details=data.reference or str(shipment_id)),
    )
    return result


def _build_letmeship_create_payload(data: CreateShipmentRequest) -> dict:
    parcel = (data.parcels or [Parcel(length=1, width=1, height=1, weight=data.weight)])[0]
    payload = {
        "pickup_address": _normalize_letmeship_address(data.pickup_address or ShippingAddress(title="Origin", line1="", city="", pincode="", country="")),
        "delivery_address": _normalize_letmeship_address(data.delivery_address or ShippingAddress(title="Destination", line1="", city="", pincode="", country="")),
        "pickup_contact": _normalize_letmeship_contact(data.pickup_contact),
        "delivery_contact": _normalize_letmeship_contact(data.delivery_contact),
        "parcels": [
            {
                "length": parcel.length,
                "width": parcel.width,
                "height": parcel.height,
                "weight": parcel.weight,
                "count": parcel.count,
            }
        ],
        "service": data.service,
        "content": data.description_of_content or "",
        "pickup_date": data.pickup_date or datetime.utcnow().strftime("%Y-%m-%d"),
    }
    return payload


def _build_sendcloud_create_payload(data: CreateShipmentRequest) -> dict:
    address = data.pickup_address or ShippingAddress(title="Origin", line1="", city="", pincode="", country="")
    delivery = data.delivery_address or ShippingAddress(title="Destination", line1="", city="", pincode="", country="")
    sender = _normalize_sendcloud_address(address)
    recipient = _normalize_sendcloud_address(delivery)
    parcels = data.parcels or [Parcel(length=1, width=1, height=1, weight=data.weight)]
    parcel_list = []
    for p in parcels:
        parcel_list.append({
            "weight": p.weight,
            "length": p.length,
            "width": p.width,
            "height": p.height,
            "name": p.description or "Parcel",
            "quantity": p.count,
        })
    payload = {
        "sender": sender,
        "recipient": recipient,
        "parcels": parcel_list,
        "service_point_id": None,
        "shipment": {
            "description": data.description_of_content or "",
        },
    }
    return payload


def _parse_create_response(provider_name: str, raw: dict, local_shipment_id: int) -> ShipmentResult:
    if provider_name.lower() == "letmeship":
        return ShipmentResult(
            shipment_id=local_shipment_id,
            provider_shipment_id=str(raw.get("id", "")),
            awb_number=raw.get("tracking_number"),
            tracking_url=raw.get("tracking_url"),
            status="booked",
            carrier="LetMeShip",
            service=raw.get("service", ""),
            label_url=raw.get("label_url"),
            cost=raw.get("price"),
            currency=raw.get("currency", "USD"),
            provider_response=raw,
            message="Shipment created successfully",
        )
    if provider_name.lower() == "sendcloud":
        parcel_ids = [p.get("id") for p in raw.get("parcels", []) if p.get("id")]
        label_url = f"/api/v1/shipping/shipments/{local_shipment_id}/label"
        return ShipmentResult(
            shipment_id=local_shipment_id,
            provider_shipment_id=str(raw.get("id", "")),
            awb_number=raw.get("tracking_number"),
            tracking_url=raw.get("tracking_url"),
            status="booked",
            carrier="SendCloud",
            service=raw.get("service", {}).get("name", ""),
            label_url=label_url,
            cost=raw.get("total_price"),
            currency=raw.get("total_price_currency", "USD"),
            provider_response=raw,
            message="Shipment created successfully",
        )
    return ShipmentResult(
        shipment_id=local_shipment_id,
        status="booked",
        carrier=provider_name,
        service="",
        provider_response=raw,
        message="Shipment created successfully",
    )


def _insert_shipment(data: CreateShipmentRequest, user: dict, raw: dict) -> int:
    import random
    now = datetime.utcnow().isoformat()
    tracking = None
    if not raw:
        tracking = f"NK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO shipments (tracking_number, reference, supplier_id, customer_id, origin, destination,
               carrier, service_type, status, weight, weight_unit, dimensions, value, currency, items_count,
               description, eta, created_at, created_by, service_provider, provider_shipment_id,
               awb_number, tracking_url, tracking_status, shipment_amount, label_url,
               pickup_from_type, delivery_to_type, provider_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tracking,
                data.reference,
                data.supplier_id,
                data.customer_id,
                data.origin,
                data.destination,
                data.service or data.provider,
                data.service_type,
                "pending",
                data.weight,
                data.weight_unit,
                data.dimensions,
                data.value,
                data.currency,
                1,
                data.description_of_content,
                None,
                now,
                user.get("id"),
                data.provider,
                None,
                None,
                None,
                "pending",
                None,
                None,
                data.pickup_from_type,
                data.delivery_to_type,
                json.dumps(raw) if raw else None,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def _insert_shipping_label(shipment_id: int, provider: str, provider_shipment_id: Optional[str], label_url: Optional[str]):
    if not provider_shipment_id or not label_url:
        return
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO shipping_labels (shipment_id, provider, provider_shipment_id, label_url, label_format, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (shipment_id, provider, str(provider_shipment_id), label_url, "PDF", now),
        )
        conn.commit()


# ========== Label ==========

def get_label(shipment_id: int) -> LabelResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
        row = cursor.fetchone()
        if not row:
            raise ShipmentBookingError("Shipment not found")
        shipment = dict(row)

    provider_name = shipment.get("service_provider") or ""
    provider_shipment_id = shipment.get("provider_shipment_id")
    label_url = shipment.get("label_url")

    if provider_shipment_id and not label_url:
        try:
            _init_providers()
            provider = get_provider(provider_name)
            raw = provider.get_label(provider_shipment_id)
            filename = f"label_{shipment_id}_{provider_shipment_id}.pdf"
            path = os.path.join(STORAGE_DIR, filename)
            with open(path, "wb") as f:
                f.write(raw)
            label_url = f"/storage/labels/{filename}"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE shipments SET label_url = ? WHERE id = ?", (label_url, shipment_id))
                conn.commit()
        except Exception as exc:
            logger.error("Label retrieval failed for %s: %s", provider_shipment_id, exc)
            _log_shipping(shipment_id, provider_name, "label", provider_shipment_id, None, str(exc), 500)
            raise LabelGenerationError(str(exc))

    if not label_url:
        label_url = f"/api/v1/shipping/shipments/{shipment_id}/label"

    _log_shipping(shipment_id, provider_name, "label", provider_shipment_id, label_url, None, 200)
    return LabelResponse(
        shipment_id=shipment_id,
        label_url=label_url,
        label_format="PDF",
        message="Label retrieved successfully",
    )


# ========== Tracking ==========

def _legacy_track_shipment(tracking_id: str) -> TrackingResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE tracking_number = ? OR id = ?", (tracking_id, tracking_id))
        row = cursor.fetchone()
        if not row:
            raise TrackingError("Shipment not found")
        shipment = dict(row)

    provider_name = shipment.get("service_provider") or ""
    provider_shipment_id = shipment.get("provider_shipment_id")
    events: List[TrackingEvent] = []
    carrier = shipment.get("carrier")
    status = shipment.get("tracking_status") or shipment.get("status", "pending")

    if provider_shipment_id:
        try:
            _init_providers()
            provider = get_provider(provider_name)
            raw = provider.get_tracking_data(provider_shipment_id)
            events = _map_tracking_events(provider_name, raw)
            status = _map_provider_status(provider_name, raw)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE shipments SET tracking_status = ?, tracking_status_info = ? WHERE id = ?",
                    (status, json.dumps(raw), shipment["id"]),
                )
                conn.commit()
            _log_shipping(shipment["id"], provider_name, "tracking", provider_shipment_id, json.dumps(raw), None, 200)
        except Exception as exc:
            logger.error("Tracking failed for %s: %s", provider_shipment_id, exc)
            _log_shipping(shipment["id"], provider_name, "tracking", provider_shipment_id, None, str(exc), 500)

    return TrackingResponse(
        shipment_id=shipment["id"],
        tracking_number=shipment.get("tracking_number"),
        status=status,
        tracking_events=events or [TrackingEvent(status=status, description="No tracking events")],
        carrier=carrier,
        provider=provider_name or None,
    )


def track_shipment(tracking_id: str) -> dict:
    resp = _legacy_track_shipment(tracking_id)
    return {
        "id": resp.shipment_id,
        "tracking_number": resp.tracking_number,
        "status": resp.status,
        "tracking_events": [e.model_dump() for e in resp.tracking_events],
    }


def _map_tracking_events(provider_name: str, raw: dict) -> List[TrackingEvent]:
    events: List[TrackingEvent] = []
    if provider_name.lower() == "letmeship":
        for ev in raw.get("events", []):
            events.append(TrackingEvent(
                status=ev.get("status", ""),
                location=ev.get("location"),
                timestamp=ev.get("timestamp"),
                description=ev.get("description"),
            ))
    elif provider_name.lower() == "sendcloud":
        for ev in raw.get("events", []):
            events.append(TrackingEvent(
                status=ev.get("status", ""),
                location=ev.get("location"),
                timestamp=ev.get("timestamp"),
                description=ev.get("message"),
            ))
    return events


def _map_provider_status(provider_name: str, raw: dict) -> str:
    status = (raw.get("status") or raw.get("tracking_status") or "").upper()
    mapping = {
        "DELIVERED": "delivered",
        "RETURNED": "returned",
        "LOST": "lost",
        "IN_TRANSIT": "in_transit",
        "ANNOUNCED": "in_transit",
        "PENDING": "pending",
        "BOOKED": "booked",
    }
    return mapping.get(status, "in_transit")


# ========== Cancellation ==========

def cancel_shipment(shipment_id: int, user: dict) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
        row = cursor.fetchone()
        if not row:
            raise ShipmentBookingError("Shipment not found")
        shipment = dict(row)
        current_status = shipment.get("tracking_status") or shipment.get("status", "pending")

    if current_status not in ("booked", "pending"):
        raise ShipmentBookingError(f"Cannot cancel shipment in status: {current_status}")

    provider_name = shipment.get("service_provider") or ""
    provider_shipment_id = shipment.get("provider_shipment_id")
    cancel_success = True
    cancel_message = "Shipment cancelled locally"

    if provider_shipment_id:
        try:
            _init_providers()
            provider = get_provider(provider_name)
            result = provider.cancel_shipment(provider_shipment_id)
            cancel_message = result.get("message", "Cancelled by provider")
            _log_shipping(shipment_id, provider_name, "cancel", provider_shipment_id, json.dumps(result), None, 200)
        except Exception as exc:
            logger.error("Provider cancel failed for %s: %s", provider_shipment_id, exc)
            cancel_success = False
            cancel_message = str(exc)
            _log_shipping(shipment_id, provider_name, "cancel", provider_shipment_id, None, str(exc), 500)
    else:
        cancel_message = "Shipment cancelled locally (no provider shipment)"

    now = datetime.utcnow().isoformat()
    local_status = "cancelled" if cancel_success else "cancellation_failed"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE shipments SET status = ?, tracking_status = ?, updated_at = ? WHERE id = ?",
            (local_status, local_status, now, shipment_id),
        )
        conn.commit()
    log_audit(
        current_user=user,
        data=AuditLogCreate(action="cancel", entity_type="shipment", entity_id=shipment_id),
    )
    return {"shipment_id": shipment_id, "status": local_status, "message": cancel_message}


# ========== Provider CRUD ==========

def create_provider(data: ShippingProviderCreate, user: dict) -> ShippingProviderResponse:
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO shipping_providers (name, provider_type, environment, enabled, is_default, config, status, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.name,
                data.provider_type,
                data.environment,
                1 if data.enabled else 0,
                1 if data.is_default else 0,
                json.dumps(data.config or {}),
                data.status,
                now,
                user.get("id"),
            ),
        )
        conn.commit()
        provider_id = cursor.lastrowid
    log_audit(
        current_user=user,
        data=AuditLogCreate(action="create", entity_type="shipping_provider", entity_id=provider_id, details=data.name),
    )
    return get_provider_by_id(provider_id)


def list_providers() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipping_providers ORDER BY id DESC")
        rows = cursor.fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["config"] = json.loads(d.get("config") or "{}")
        result.append(d)
    return result


def get_provider_by_id(provider_id: int) -> ShippingProviderResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipping_providers WHERE id = ?", (provider_id,))
        row = cursor.fetchone()
        if not row:
            raise ProviderNotFoundError("Provider not found")
    d = dict(row)
    d["config"] = json.loads(d.get("config") or "{}")
    return ShippingProviderResponse(**d)


def update_provider(provider_id: int, data: ShippingProviderUpdate) -> ShippingProviderResponse:
    fields = {}
    if data.name is not None:
        fields["name"] = data.name
    if data.provider_type is not None:
        fields["provider_type"] = data.provider_type
    if data.environment is not None:
        fields["environment"] = data.environment
    if data.enabled is not None:
        fields["enabled"] = 1 if data.enabled else 0
    if data.is_default is not None:
        fields["is_default"] = 1 if data.is_default else 0
    if data.config is not None:
        fields["config"] = json.dumps(data.config)
    if data.status is not None:
        fields["status"] = data.status

    if not fields:
        return get_provider_by_id(provider_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [datetime.utcnow().isoformat(), provider_id]
        cursor.execute(f"UPDATE shipping_providers SET {set_clause}, updated_at = ? WHERE id = ?", values)
        conn.commit()
    log_audit(
        current_user=None,
        data=AuditLogCreate(action="update", entity_type="shipping_provider", entity_id=provider_id),
    )
    return get_provider_by_id(provider_id)


def delete_provider(provider_id: int) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shipping_providers WHERE id = ?", (provider_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ProviderNotFoundError("Provider not found")
    log_audit(
        current_user=None,
        data=AuditLogCreate(action="delete", entity_type="shipping_provider", entity_id=provider_id),
    )


# ========== Parcel Template CRUD ==========

def create_parcel_template(data: ParcelTemplateCreate, user: dict) -> ParcelTemplateResponse:
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO shipping_parcel_templates (name, length, width, height, weight, description, is_active, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.name, data.length, data.width, data.height, data.weight, data.description, 1 if data.is_active else 0, now, now),
        )
        conn.commit()
        template_id = cursor.lastrowid
    template_name = getattr(data, "name", None)
    if not isinstance(template_name, str):
        template_name = None
    log_audit(
        current_user=user,
        data=AuditLogCreate(action="create", entity_type="parcel_template", entity_id=template_id, details=template_name),
    )
    return get_parcel_template(template_id)


def list_parcel_templates() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipping_parcel_templates ORDER BY id DESC")
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


def get_parcel_template(template_id: int) -> ParcelTemplateResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipping_parcel_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        if not row:
            raise ShippingError("Parcel template not found")
    return ParcelTemplateResponse(**dict(row))


def update_parcel_template(template_id: int, data: ParcelTemplateUpdate) -> ParcelTemplateResponse:
    fields = {}
    if data.name is not None:
        fields["name"] = data.name
    if data.length is not None:
        fields["length"] = data.length
    if data.width is not None:
        fields["width"] = data.width
    if data.height is not None:
        fields["height"] = data.height
    if data.weight is not None:
        fields["weight"] = data.weight
    if data.description is not None:
        fields["description"] = data.description
    if data.is_active is not None:
        fields["is_active"] = 1 if data.is_active else 0

    if not fields:
        return get_parcel_template(template_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [datetime.utcnow().isoformat(), template_id]
        cursor.execute(f"UPDATE shipping_parcel_templates SET {set_clause}, updated_at = ? WHERE id = ?", values)
        conn.commit()
    log_audit(
        current_user=None,
        data=AuditLogCreate(action="update", entity_type="parcel_template", entity_id=template_id),
    )
    return get_parcel_template(template_id)


def delete_parcel_template(template_id: int) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shipping_parcel_templates WHERE id = ?", (template_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ShippingError("Parcel template not found")
    log_audit(
        current_user=None,
        data=AuditLogCreate(action="delete", entity_type="parcel_template", entity_id=template_id),
    )


# ========== Audit Logging ==========

def _log_shipping(
    shipment_id: Optional[int],
    provider: str,
    action: str,
    request_payload: Optional[str],
    response_payload: Optional[str],
    error_message: Optional[str],
    status_code: int,
):
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO shipping_logs (shipment_id, provider, action, request_payload, response_payload, error_message, status_code, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (shipment_id, provider, action, request_payload, response_payload, error_message, status_code, now),
        )
        conn.commit()


# ========== List Shipments ==========

def list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM shipments WHERE 1=1"
        params = []
        if status:
            query += " AND (status = ? OR tracking_status = ?)"
            params.extend([status, status])
        if customer_id:
            query += " AND customer_id = ?"
            params.append(customer_id)
        if supplier_id:
            query += " AND supplier_id = ?"
            params.append(supplier_id)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


def _legacy_get_shipment(shipment_id: int) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
        row = cursor.fetchone()
        if not row:
            raise ShippingError("Shipment not found")
    result = dict(row)
    if result.get("origin") is None:
        result["origin"] = ""
    if result.get("destination") is None:
        result["destination"] = ""
    return result


def get_shipment(shipment_id: int) -> dict:
    return _legacy_get_shipment(shipment_id)


def update_shipment_status(shipment_id: int, status: str) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM shipments WHERE id = ?", (shipment_id,))
        if not cursor.fetchone():
            raise ShippingError("Shipment not found")
        cursor.execute(
            "UPDATE shipments SET status = ?, tracking_status = ?, updated_at = ? WHERE id = ?",
            (status, status, now, shipment_id),
        )
        conn.commit()
    log_audit(
        current_user=None,
        data=AuditLogCreate(action="update", entity_type="shipment", entity_id=shipment_id),
    )
    return {"message": "Shipment updated successfully"}


def get_rates(request) -> list:
    return fetch_rates(request)


def _legacy_list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM shipments WHERE 1=1"
        params = []
        if status:
            query += " AND (status = ? OR tracking_status = ?)"
            params.extend([status, status])
        if customer_id:
            query += " AND customer_id = ?"
            params.append(customer_id)
        if supplier_id:
            query += " AND supplier_id = ?"
            params.append(supplier_id)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


def list_shipments(**kwargs) -> list:
    return _legacy_list_shipments(**kwargs)


def _legacy_create_shipment(data: CreateShipmentRequest, user: dict) -> ShipmentResult:
    _init_providers()
    provider = None
    raw = {}
    try:
        provider = get_provider(data.provider)
    except ProviderNotFoundError:
        logger.warning("Provider '%s' not found, creating local-only shipment", data.provider)

    if provider:
        try:
            validate_parcels(data.parcels)
            if data.pickup_contact:
                validate_phone(data.pickup_contact.phone)
            if data.delivery_contact:
                validate_phone(data.delivery_contact.phone)
            if data.pickup_address:
                validate_address(data.pickup_address)
            if data.delivery_address:
                validate_address(data.delivery_address)
        except ValidationError as exc:
            raise ShipmentBookingError(str(exc))

        ptype = provider.__class__.__name__.lower()
        if "letmeship" in ptype:
            payload = _build_letmeship_create_payload(data)
        else:
            payload = _build_sendcloud_create_payload(data)

        try:
            raw = provider.create_shipment(payload)
        except Exception as exc:
            _log_shipping(None, data.provider, "create", json.dumps(payload), None, str(exc), 500)
            raise ShipmentBookingError(str(exc))

    shipment_id = _insert_shipment(data, user, raw)
    _log_shipping(shipment_id, data.provider, "create", json.dumps(raw), json.dumps(raw), None, 200 if raw else 0)

    result = _parse_create_response(data.provider, raw, shipment_id)
    if raw:
        _insert_shipping_label(shipment_id, data.provider, result.provider_shipment_id, result.label_url)
    log_audit(
        current_user=user,
        data=AuditLogCreate(action="create", entity_type="shipment", entity_id=shipment_id, details=data.reference or str(shipment_id)),
    )
    return result


def create_shipment(data, current_user: dict) -> dict:
    from app.schemas.shipment import ShipmentCreate
    if isinstance(data, dict):
        create_data = ShipmentCreate(**data)
    else:
        create_data = data
    req = CreateShipmentRequest(
        provider=data.carrier or "LetMeShip",
        service=data.service_type or "Standard",
        origin=data.origin or "",
        destination=data.destination or "",
        weight=data.weight or 1,
        weight_unit=data.weight_unit or "kg",
        dimensions=data.dimensions,
        value=data.value,
        reference=data.reference,
        supplier_id=data.supplier_id,
        customer_id=data.customer_id,
        currency=data.currency or "USD",
        service_type=data.service_type,
    )
    result = _legacy_create_shipment(req, current_user)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tracking_number FROM shipments WHERE id = ?", (result.shipment_id,))
        row = cursor.fetchone()
        tracking = row["tracking_number"] if row else str(result.shipment_id)
    _send_shipping_notification(
        template_id=3,
        user_id=current_user.get("id") if current_user else None,
        variables={"shipment_id": result.shipment_id, "tracking_number": tracking},
        current_user=current_user,
    )
    return {
        "id": result.shipment_id,
        "tracking_number": tracking,
        "message": result.message,
    }


def update_shipment(shipment_id: int, data, current_user: dict) -> dict:
    from app.schemas.shipment import ShipmentUpdate
    if isinstance(data, dict):
        update_data = ShipmentUpdate(**data)
    else:
        update_data = data
    if update_data.status:
        result = update_shipment_status(shipment_id, update_data.status)
        _send_shipping_notification(
            template_id=4,
            user_id=current_user.get("id") if current_user else None,
            variables={"shipment_id": shipment_id, "status": update_data.status},
            current_user=current_user,
        )
        return result
    return {"message": "Shipment updated successfully"}


def _legacy_get_label(shipment_id: int) -> LabelResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
        row = cursor.fetchone()
        if not row:
            raise ShipmentBookingError("Shipment not found")
        shipment = dict(row)

    provider_name = shipment.get("service_provider") or ""
    provider_shipment_id = shipment.get("provider_shipment_id")
    label_url = shipment.get("label_url")

    if provider_shipment_id and not label_url:
        try:
            _init_providers()
            provider = get_provider(provider_name)
            raw = provider.get_label(provider_shipment_id)
            filename = f"label_{shipment_id}_{provider_shipment_id}.pdf"
            path = os.path.join(STORAGE_DIR, filename)
            with open(path, "wb") as f:
                f.write(raw)
            label_url = f"/storage/labels/{filename}"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE shipments SET label_url = ? WHERE id = ?", (label_url, shipment_id))
                conn.commit()
        except Exception as exc:
            logger.error("Label retrieval failed for %s: %s", provider_shipment_id, exc)
            _log_shipping(shipment_id, provider_name, "label", provider_shipment_id, None, str(exc), 500)
            raise LabelGenerationError(str(exc))

    if not label_url:
        label_url = f"/api/v1/shipping/shipments/{shipment_id}/label"

    _log_shipping(shipment_id, provider_name, "label", provider_shipment_id, label_url, None, 200)
    return LabelResponse(
        shipment_id=shipment_id,
        label_url=label_url,
        label_format="PDF",
        message="Label retrieved successfully",
    )


def get_label(shipment_id: int) -> dict:
    resp = _legacy_get_label(shipment_id)
    return {
        "shipment_id": resp.shipment_id,
        "label_url": resp.label_url,
        "message": resp.message,
    }


# ========== Delivery Confirmation Capability ==========


def record_delivery_confirmation(
    shipment_id: int,
    export_workflow_id: int,
    confirmed_by: int,
    proof_reference: Optional[str] = None,
    event_data: Optional[dict] = None,
) -> dict:
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM shipments WHERE id = ?", (shipment_id,))
            shipment = cursor.fetchone()
            if not shipment or shipment["status"] not in ("delivered", "in_transit"):
                raise ValueError("Shipment not eligible for delivery confirmation")

            cursor.execute(
                "SELECT shipment_id FROM export_workflows WHERE id = ?",
                (export_workflow_id,),
            )
            wf = cursor.fetchone()
            if not wf or wf["shipment_id"] != shipment_id:
                raise ValueError("export_workflow_id does not match shipment_id")

            cursor.execute(
                """SELECT id FROM shipping_logs
                   WHERE shipment_id = ? AND event_type = 'delivery_confirmed'
                   AND delivery_confirmed_by = ? AND export_workflow_id = ?""",
                (shipment_id, confirmed_by, export_workflow_id),
            )
            if cursor.fetchone():
                raise ValueError("Duplicate delivery confirmation")

            cursor.execute(
                """INSERT INTO shipping_logs
                   (shipment_id, provider, action, event_type, delivery_confirmed_by, proof_of_delivery_reference,
                    export_workflow_id, event_data, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    shipment_id,
                    "internal",
                    "delivery_confirmed",
                    "delivery_confirmed",
                    confirmed_by,
                    proof_reference,
                    export_workflow_id,
                    json.dumps(event_data) if event_data else None,
                    now,
                ),
            )
            log_id = cursor.lastrowid

            cursor.execute(
                "UPDATE export_workflows SET delivery_confirmed_at = ? WHERE id = ?",
                (now, export_workflow_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    log_audit(
        current_user={"id": confirmed_by},
        data=AuditLogCreate(
            action="delivery_confirmation",
            entity_type="shipping_log",
            entity_id=log_id,
            details=json.dumps({
                "shipment_id": shipment_id,
                "export_workflow_id": export_workflow_id,
                "delivery_confirmed_by": confirmed_by,
                "proof_reference": proof_reference,
            }),
        ),
    )

    return {
        "id": log_id,
        "shipment_id": shipment_id,
        "export_workflow_id": export_workflow_id,
        "event_type": "delivery_confirmed",
        "delivery_confirmed_by": confirmed_by,
        "proof_of_delivery_reference": proof_reference,
        "created_at": now,
    }


def get_delivery_history(
    shipment_id: Optional[int] = None,
    export_workflow_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[dict]:
    query = "SELECT * FROM shipping_logs WHERE event_type = 'delivery_confirmed'"
    params = []
    if shipment_id is not None:
        query += " AND shipment_id = ?"
        params.append(shipment_id)
    if export_workflow_id is not None:
        query += " AND export_workflow_id = ?"
        params.append(export_workflow_id)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return [dict(r) for r in rows]
