"""
SendCloud HTTP Client
- API key/secret auth (Basic Auth)
- httpx + tenacity retry
- Endpoints: shipping-options, shipments/announce, labels, parcels, cancel
"""

import httpx
import logging
from typing import Optional, Dict, Any, List

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("shipping.sendcloud")


class SendCloudError(Exception):
    def __init__(self, status_code: int, message: str, details: Optional[Any] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"[{status_code}] {message}")


class SendCloudClient:
    _RETRY_ATTEMPTS = 3
    _RETRY_WAIT_MULTIPLIER = 1
    _RETRY_WAIT_MIN = 1
    _RETRY_WAIT_MAX = 10

    def __init__(self, public_key: str, secret_key: str, environment: str = "Pre-Production"):
        self.public_key = public_key
        self.secret_key = secret_key
        self.environment = environment
        self.base_url = (
            "https://panel.sendcloud.sc/api"
            if environment == "Production"
            else "https://panel.sendcloud.sc/api"
        )
        self._client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={"content-type": "application/json; charset=utf-8"},
            auth=(public_key, secret_key),
        )
        self.enabled = True

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("SendCloud request retry %d/%d", rs.attempt_number, SendCloudClient._RETRY_ATTEMPTS),
    )
    def _post_with_retry(self, url: str, json: dict, headers: Optional[dict] = None) -> httpx.Response:
        return self._client.post(url, json=json, headers=headers)

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("SendCloud request retry %d/%d", rs.attempt_number, SendCloudClient._RETRY_ATTEMPTS),
    )
    def _get_with_retry(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> httpx.Response:
        return self._client.get(url, headers=headers, params=params)

    def get_shipping_options(self, payload: dict) -> List[Dict[str, Any]]:
        response = self._post_with_retry(
            f"{self.base_url}/v3/shipping-options",
            json=payload,
        )
        if response.status_code != 200:
            raise SendCloudError(response.status_code, f"SendCloud rates failed: {response.text[:500]}")
        data = response.json()
        return data.get("shipping_methods", [])

    def announce_shipment(self, payload: dict) -> Dict[str, Any]:
        response = self._post_with_retry(
            f"{self.base_url}/v3/shipments/announce",
            json=payload,
        )
        if response.status_code not in (200, 201):
            raise SendCloudError(response.status_code, f"SendCloud create shipment failed: {response.text[:500]}")
        return response.json()

    def get_label(self, parcel_ids: List[int]) -> bytes:
        ids_str = ",".join(str(pid) for pid in parcel_ids)
        response = self._get_with_retry(
            f"{self.base_url}/v2/labels/{ids_str}",
        )
        if response.status_code != 200:
            raise SendCloudError(response.status_code, f"SendCloud label failed: {response.text[:500]}")
        return response.content

    def get_parcel(self, parcel_id: int) -> Dict[str, Any]:
        response = self._get_with_retry(
            f"{self.base_url}/v2/parcels/{parcel_id}",
        )
        if response.status_code != 200:
            raise SendCloudError(response.status_code, f"SendCloud get parcel failed: {response.text[:500]}")
        return response.json()

    def cancel_shipment(self, shipment_id: int) -> Dict[str, Any]:
        response = self._post_with_retry(
            f"{self.base_url}/v3/shipments/{shipment_id}/cancel",
            json={},
        )
        if response.status_code != 200:
            raise SendCloudError(response.status_code, f"SendCloud cancel failed: {response.text[:500]}")
        return response.json()

    def close(self):
        self._client.close()
