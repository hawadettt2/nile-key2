"""
Shipping Provider Base + Registry
Abstract interface and provider registration for the Shipping Engine.
"""

from abc import ABC, abstractmethod


class ShippingError(Exception):
    """Base shipping error."""
    pass


class ProviderNotFoundError(ShippingError):
    pass


class RateFetchError(ShippingError):
    pass


class ShipmentBookingError(ShippingError):
    pass


class LabelGenerationError(ShippingError):
    pass


class TrackingError(ShippingError):
    pass


class ValidationError(ShippingError):
    pass


class ShippingProvider(ABC):
    @abstractmethod
    def get_available_services(self, request) -> list:
        pass

    @abstractmethod
    def create_shipment(self, request) -> dict:
        pass

    @abstractmethod
    def get_label(self, shipment_id: str) -> dict:
        pass

    @abstractmethod
    def get_tracking_data(self, shipment_id: str) -> dict:
        pass

    @abstractmethod
    def cancel_shipment(self, shipment_id: str) -> dict:
        pass


PROVIDERS: dict[str, ShippingProvider] = {}


def register_provider(name: str, provider: ShippingProvider) -> None:
    PROVIDERS[name] = provider


def get_provider(name: str) -> ShippingProvider:
    provider = PROVIDERS.get(name)
    if not provider:
        raise ProviderNotFoundError(f"Shipping provider '{name}' not found")
    return provider


def get_enabled_providers() -> list[ShippingProvider]:
    return [p for p in PROVIDERS.values() if getattr(p, "enabled", False)]
