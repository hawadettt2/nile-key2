"""
Shipping Engine — Compatibility Shim
Existing imports continue to work while the new shipping package is adopted.
"""

from app.services.shipping import (
    get_rates,
    list_shipments,
    track_shipment as track_shipment_legacy,
    get_shipment as get_shipment_legacy,
    create_shipment as create_shipment_legacy,
    update_shipment as update_shipment_legacy,
    get_label as get_label_legacy,
)


def get_rates_legacy(request):
    return get_rates(request)


def track_shipment(tracking_id: str) -> dict:
    return track_shipment_legacy(tracking_id)


def get_shipment(shipment_id: int) -> dict:
    return get_shipment_legacy(shipment_id)


def list_shipments_legacy_api(**kwargs) -> list:
    return list_shipments(**kwargs)


def create_shipment(data, current_user: dict) -> dict:
    return create_shipment_legacy(data, current_user)


def update_shipment(shipment_id: int, data, current_user: dict) -> dict:
    return update_shipment_legacy(shipment_id, data, current_user)


def get_label(shipment_id: int) -> dict:
    return get_label_legacy(shipment_id)
