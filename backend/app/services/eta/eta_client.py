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

    def __init__(self, auth_config: ETAAuthConfig):
        self.auth_config = auth_config
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={"content-type": "application/json; charset=utf-8"},
        )

    def _get_token(self) -> str:
        """Get or refresh OAuth2 access token using client credentials flow."""
        if self._access_token and self._token_expires_at:
            # Refresh if within 3 minutes of expiry
            if datetime.utcnow() < self._token_expires_at - timedelta(minutes=3):
                return self._access_token

        return self._refresh_token()

    def _refresh_token(self) -> str:
        """Request new access token from ETA IDP."""
        response = self._client.post(
            self.auth_config.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.auth_config.client_id,
                "client_secret": self.auth_config.client_secret,
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
        logger.info("ETA access token refreshed, expires in %ds", expires_in)
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
            f"{self.auth_config.base_url}/documentsubmissions",
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
            f"{self.auth_config.base_url}/receiptsubmissions",
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
            f"{self.auth_config.base_url}/documents/state/{uuid}/state",
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
            f"{self.auth_config.base_url}/documents/{uuid}/raw",
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
            f"{self.auth_config.base_url}/documentSubmissions/{submission_id}",
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
            f"{self.auth_config.base_url}/receiptsubmissions/{submission_id}/details",
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
            f"{self.auth_config.base_url}/receipts/{uuid}/raw/",
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
            f"{self.auth_config.base_url}/documents/{uuid}/pdf",
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
