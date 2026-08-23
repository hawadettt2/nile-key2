"""
LetMeShip HTTP Client
- Basic auth (api_id, api_password)
- httpx + tenacity retry
- Endpoints: available, shipments, tracking, documents/labels
"""

import httpx
import logging
from typing import Optional, Dict, Any, List

from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("shipping.letmeship")


class LetMeShipError(Exception):
    def __init__(self, status_code: int, message: str, details: Optional[Any] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"[{status_code}] {message}")


class LetMeShipClient:
    _RETRY_ATTEMPTS = 3
    _RETRY_WAIT_MULTIPLIER = 1
    _RETRY_WAIT_MIN = 1
    _RETRY_WAIT_MAX = 10

    def __init__(
        self,
        api_id: str = "",
        api_password: str = "",
        environment: str = "Pre-Production",
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        self._credential_store = credential_store
        self.environment = environment
        self.base_url = (
            "https://api.test.letmeship.com/v1"
            if environment == "Pre-Production"
            else "https://api.letmeship.com/v1"
        )

        if credential_store is not None:
            credential = credential_store.get("letmeship_api_id")
            if credential is not None:
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    loop.run_until_complete(credential.on_before_use())
                finally:
                    loop.close()
                self.api_id = credential.get_username()
                self.api_password = credential.get_password()
            else:
                self.api_id = api_id
                self.api_password = api_password
        else:
            self.api_id = api_id
            self.api_password = api_password

        self._client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={"content-type": "application/json; charset=utf-8"},
            auth=(self.api_id, self.api_password),
        )
        self.enabled = True

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("LetMeShip request retry %d/%d", rs.attempt_number, LetMeShipClient._RETRY_ATTEMPTS),
    )
    def _post_with_retry(self, url: str, json: dict, headers: Optional[dict] = None) -> httpx.Response:
        return self._client.post(url, json=json, headers=headers)

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("LetMeShip request retry %d/%d", rs.attempt_number, LetMeShipClient._RETRY_ATTEMPTS),
    )
    def _get_with_retry(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> httpx.Response:
        return self._client.get(url, headers=headers, params=params)

    def get_available_services(self, payload: dict) -> List[Dict[str, Any]]:
        response = self._post_with_retry(
            f"{self.base_url}/available",
            json=payload,
        )
        if response.status_code != 200:
            logger.error(
                "LetMeShip get_available_services failed: status=%s",
                response.status_code,
            )
            raise LetMeShipError(response.status_code, "LetMeShip rates failed")
        data = response.json()
        return data.get("services", [])

    def create_shipment(self, payload: dict) -> Dict[str, Any]:
        response = self._post_with_retry(
            f"{self.base_url}/shipments",
            json=payload,
        )
        if response.status_code not in (200, 201):
            logger.error(
                "LetMeShip create_shipment failed: status=%s",
                response.status_code,
            )
            raise LetMeShipError(response.status_code, "LetMeShip create shipment failed")
        return response.json()

    def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        response = self._get_with_retry(
            f"{self.base_url}/shipments/{shipment_id}",
        )
        if response.status_code != 200:
            logger.error(
                "LetMeShip get_shipment failed: status=%s",
                response.status_code,
            )
            raise LetMeShipError(response.status_code, "LetMeShip get shipment failed")
        return response.json()

    def get_label(self, shipment_id: str) -> bytes:
        response = self._get_with_retry(
            f"{self.base_url}/shipments/{shipment_id}/documents",
            params={"types": "LABEL"},
        )
        if response.status_code != 200:
            logger.error(
                "LetMeShip get_label failed: status=%s",
                response.status_code,
            )
            raise LetMeShipError(response.status_code, "LetMeShip label failed")
        return response.content

    def get_tracking_data(self, shipment_id: str) -> Dict[str, Any]:
        response = self._get_with_retry(
            f"{self.base_url}/tracking",
            params={"shipmentid": shipment_id},
        )
        if response.status_code != 200:
            logger.error(
                "LetMeShip get_tracking_data failed: status=%s",
                response.status_code,
            )
            raise LetMeShipError(response.status_code, "LetMeShip tracking failed")
        return response.json()

    def close(self):
        self._client.close()
