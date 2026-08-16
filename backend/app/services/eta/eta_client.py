"""
ETA HTTP Client
- OAuth2 client credentials flow
- Invoice submit/cancel/status endpoints
- Receipt submit/status endpoints
- PDF download
- Retry logic via httpx + tenacity
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.credentials.client_id_secret_credential import ClientIdSecretCredential
from app.core.credentials.credential_store import CredentialStore
from app.schemas.eta import ETAAuthConfig, InvoiceSubmit, ReceiptSubmit, ReceiptsResponse

logger = logging.getLogger("eta")


class ETAHttpError(Exception):
    def __init__(self, status_code: int, message: str, details: Optional[List[Dict]] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or []
        super().__init__(f"[{status_code}] {message}")


class ETAClient:
    """HTTP client for Egyptian Tax Authority ETA API with retry and error handling."""
    
    # Retry configuration matching reference repo (3 retries with exponential backoff)
    _RETRY_ATTEMPTS = 3
    _RETRY_WAIT_MULTIPLIER = 1
    _RETRY_WAIT_MIN = 1
    _RETRY_WAIT_MAX = 10

    def __init__(
        self,
        auth_config: ETAAuthConfig,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        self._credential_store = credential_store
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={"content-type": "application/json; charset=utf-8"},
        )

        if credential_store is not None:
            client_id_credential = credential_store.get("eta_client_id")
            client_secret_credential = credential_store.get("eta_client_secret")

            if client_id_credential is None or client_secret_credential is None:
                logger.warning("ETA credentials missing from CredentialStore; client will not authenticate")
                self._auth_config = auth_config
            else:
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    loop.run_until_complete(client_id_credential.on_before_use())
                    loop.run_until_complete(client_secret_credential.on_before_use())
                finally:
                    loop.close()

                self._auth_config = ETAAuthConfig(
                    client_id=client_id_credential.get_client_id(),
                    client_secret=client_secret_credential.get_client_secret(),
                    environment=auth_config.environment,
                    pos_serial=auth_config.pos_serial,
                    pos_os_version=auth_config.pos_os_version,
                )
        else:
            self._auth_config = auth_config

    def _get_token(self) -> str:
        """Get or refresh OAuth2 access token using client credentials flow."""
        if self._access_token and self._token_expires_at:
            # Refresh if within 3 minutes of expiry
            if datetime.utcnow() < self._token_expires_at - timedelta(minutes=3):
                return self._access_token

        return self._refresh_token()

    def _refresh_token(self) -> str:
        """Request new access token from ETA IDP."""
        client_id_credential = self._credential_store.get("eta_client_id") if self._credential_store else None
        client_secret_credential = self._credential_store.get("eta_client_secret") if self._credential_store else None

        if client_id_credential is not None and client_secret_credential is not None:
            client_id = client_id_credential.get_client_id()
            client_secret = client_secret_credential.get_client_secret()
            masked_client_id = client_id_credential.mask() if client_id_credential.is_empty() is False else "***"
            masked_client_secret = client_secret_credential.mask()
        else:
            client_id = self._auth_config.client_id
            client_secret = self._auth_config.client_secret
            masked_client_id = client_id[:4] + "***" if len(client_id) > 4 else "***"
            masked_client_secret = client_secret[:4] + "***" if len(client_secret) > 4 else "***"

        response = self._client.post(
            self._auth_config.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "InvoicingAPI",
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Token refresh failed: {response.text[:500]}",
            )

        data = response.json()
        self._access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        logger.info(
            "ETA access token refreshed for client_id=%s, expires in %ds",
            masked_client_id,
            expires_in,
        )

        if client_id_credential is not None and client_secret_credential is not None:
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(client_id_credential.on_after_use())
                loop.run_until_complete(client_secret_credential.on_after_use())
            finally:
                loop.close()

        return self._access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "content-type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self._get_token()}",
        }

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("ETA request retry %d/%d", rs.attempt_number, _RETRY_ATTEMPTS),
    )
    def _post_with_retry(self, url: str, json: dict, headers: dict) -> httpx.Response:
        """POST with automatic retry on transient failures."""
        return self._client.post(url, json=json, headers=headers)

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=_RETRY_WAIT_MULTIPLIER, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=lambda rs: logger.warning("ETA request retry %d/%d", rs.attempt_number, _RETRY_ATTEMPTS),
    )
    def _get_with_retry(self, url: str, headers: dict, params: Optional[dict] = None) -> httpx.Response:
        """GET with automatic retry on transient failures."""
        return self._client.get(url, headers=headers, params=params)

    def submit_invoices(self, invoices: List[InvoiceSubmit], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Submit one or more e-invoices to ETA."""
        headers = self._headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        payload = {"documents": [inv.model_dump(exclude_none=True) for inv in invoices]}
        response = self._post_with_retry(
            f"{self._auth_config.base_url}/documentsubmissions",
            json=payload,
            headers=headers,
        )

        if response.status_code not in (200, 202):
            error_data = response.json() if response.text else {}
            message = error_data.get("message", response.text[:500])
            details = error_data.get("details", [])
            raise ETAHttpError(response.status_code, message, details)

        result = response.json()
        logger.info(
            "Submitted %d invoices, submission_id=%s",
            len(invoices),
            result.get("submissionId"),
        )
        return result

    def submit_receipts(self, receipts: List[ReceiptSubmit], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Submit one or more e-receipts to ETA."""
        headers = self._headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        payload = {"receipts": [r.model_dump(exclude_none=True) for r in receipts]}
        response = self._post_with_retry(
            f"{self._auth_config.base_url}/receiptsubmissions",
            json=payload,
            headers=headers,
        )

        if response.status_code not in (200, 202):
            error_data = response.json() if response.text else {}
            message = error_data.get("message", response.text[:500])
            details = error_data.get("details", [])
            raise ETAHttpError(response.status_code, message, details)

        result = response.json()
        logger.info(
            "Submitted %d receipts, submission_id=%s",
            len(receipts),
            result.get("submissionId"),
        )
        return result

    def cancel_document(self, uuid: str, reason: str) -> Dict[str, Any]:
        """Cancel a submitted document by UUID."""
        response = self._client.put(
            f"{self._auth_config.base_url}/documents/state/{uuid}/state",
            json={"status": "cancelled", "reason": reason},
            headers=self._headers(),
        )

        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            message = error_data.get("message", response.text[:500])
            details = error_data.get("details", [])
            raise ETAHttpError(response.status_code, message, details)

        logger.info("Document %s cancelled", uuid)
        return response.json()

    def get_document_status(self, uuid: str) -> Dict[str, Any]:
        """Get raw document status by UUID."""
        response = self._get_with_retry(
            f"{self._auth_config.base_url}/documents/{uuid}/raw",
            headers=self._headers(),
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Failed to get document status: {response.text[:500]}",
            )

        return response.json()

    def get_submission_details(self, submission_id: str) -> Dict[str, Any]:
        """Get submission details by submission ID."""
        response = self._get_with_retry(
            f"{self._auth_config.base_url}/documentSubmissions/{submission_id}",
            headers=self._headers(),
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Failed to get submission details: {response.text[:500]}",
            )

        return response.json()

    def get_receipt_submission_details(self, submission_id: str) -> Dict[str, Any]:
        """Get receipt submission details with pagination."""
        response = self._get_with_retry(
            f"{self._auth_config.base_url}/receiptsubmissions/{submission_id}/details",
            params={"PageNo": 1, "PageSize": 100},
            headers=self._headers(),
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Failed to get receipt submission details: {response.text[:500]}",
            )

        return response.json()

    def get_receipt_status(self, uuid: str) -> Dict[str, Any]:
        """Get individual receipt status by UUID."""
        response = self._get_with_retry(
            f"{self._auth_config.base_url}/receipts/{uuid}/raw/",
            headers=self._headers(),
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Failed to get receipt status: {response.text[:500]}",
            )

        return response.json()

    def download_pdf(self, uuid: str) -> bytes:
        """Download ETA document PDF."""
        response = self._get_with_retry(
            f"{self._auth_config.base_url}/documents/{uuid}/pdf",
            headers=self._headers(),
        )

        if response.status_code != 200:
            raise ETAHttpError(
                response.status_code,
                f"Failed to download PDF: {response.text[:500]}",
            )

        logger.info("PDF downloaded for document %s", uuid)
        return response.content

    def close(self):
        """Close underlying HTTP client."""
        self._client.close()
