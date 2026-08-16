import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential

logger = logging.getLogger(__name__)


class FaostatApiClient:
    """Isolated HTTP client for FAOSTAT API with JWT authentication lifecycle.

    This client implements the official FAOSTAT authentication flow:
    - POST /auth/login with username/password
    - Receive JWT Bearer token (expires after 60 minutes)
    - Use token in Authorization header
    - Re-authenticate on 401 or expiry

    This client is intentionally kept outside the DEM core and outside
    ``KnowledgeProvider``. It is owned by the FAOSTAT adapter boundary and
    may change without affecting DEM core or the provider contract.
    """

    def __init__(
        self,
        base_url: str,
        credential_store: Optional[CredentialStore] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._credential_store = credential_store
        self._username = username
        self._password = password
        self._timeout_seconds = timeout_seconds

        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()
        self._re_auth_in_progress = False

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
        }
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    async def _login(self) -> None:
        if self._credential_store is not None:
            username_credential = self._credential_store.get("faostat_username")
            password_credential = self._credential_store.get("faostat_password")

            if username_credential is None or password_credential is None:
                logger.warning("FAOSTAT credentials missing; cannot acquire access token")
                self._access_token = None
                self._token_expires_at = None
                return

            await username_credential.on_before_use()
            await password_credential.on_before_use()

            username = username_credential.get_username()
            password = password_credential.get_password()
        else:
            if not self._username or not self._password:
                logger.warning("FAOSTAT credentials missing; cannot acquire access token")
                self._access_token = None
                self._token_expires_at = None
                return

            username = self._username
            password = self._password

        login_url = f"{self._base_url}/auth/login"
        data = {
            "username": username,
            "password": password,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(
                login_url,
                headers=headers,
                data=data,
            )

        if response.status_code != 200:
            logger.warning("FAOSTAT login failed with status %s", response.status_code)
            self._access_token = None
            self._token_expires_at = None
            response.raise_for_status()

        try:
            payload = response.json()
        except ValueError:
            logger.warning("FAOSTAT login returned non-JSON response")
            self._access_token = None
            self._token_expires_at = None
            raise ValueError("FAOSTAT login response is not valid JSON")

        auth_result = payload.get("AuthenticationResult")
        if not isinstance(auth_result, dict):
            logger.warning("FAOSTAT login response missing AuthenticationResult")
            self._access_token = None
            self._token_expires_at = None
            raise ValueError("FAOSTAT login response missing AuthenticationResult")

        access_token = auth_result.get("AccessToken")
        if not access_token or not isinstance(access_token, str):
            logger.warning("FAOSTAT login response missing AccessToken")
            self._access_token = None
            self._token_expires_at = None
            raise ValueError("FAOSTAT login response missing AccessToken")

        self._access_token = access_token
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=55)

        if self._credential_store is not None:
            await username_credential.on_after_use()
            await password_credential.on_after_use()

    async def _ensure_token(self) -> None:
        if self._access_token and self._token_expires_at:
            if datetime.now(timezone.utc) < self._token_expires_at:
                return

        async with self._auth_lock:
            if self._re_auth_in_progress:
                return
            self._re_auth_in_progress = True
            try:
                await self._login()
            finally:
                self._re_auth_in_progress = False

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not path:
            raise ValueError("path is required for FAOSTAT API request")

        url = f"{self._base_url}{path}" if path.startswith("/") else f"{self._base_url}/{path}"
        return await self._request_with_retry(method=method, url=url, params=params)

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        max_429_attempts = 3
        max_network_attempts = 2
        max_5xx_attempts = 2
        max_auth_attempts = 1
        backoff_429 = 1.0
        backoff_network = 2.0
        backoff_5xx = 2.0

        attempt_429 = 0
        attempt_network = 0
        attempt_5xx = 0
        attempt_auth = 0

        while True:
            try:
                await self._ensure_token()
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self._headers(),
                        params=params,
                    )

                    if response.status_code == 401 and attempt_auth < max_auth_attempts:
                        attempt_auth += 1
                        await self._login()
                        continue

                    if response.status_code == 429:
                        attempt_429 += 1
                        if attempt_429 < max_429_attempts:
                            await asyncio.sleep(backoff_429)
                            backoff_429 *= 2
                            continue
                        response.raise_for_status()

                    if 500 <= response.status_code < 600:
                        attempt_5xx += 1
                        if attempt_5xx < max_5xx_attempts:
                            await asyncio.sleep(backoff_5xx)
                            backoff_5xx *= 2
                            continue
                        response.raise_for_status()

                    response.raise_for_status()
                    return response.json()

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                attempt_network += 1
                if attempt_network < max_network_attempts:
                    await asyncio.sleep(backoff_network)
                    backoff_network *= 2
                    continue
                raise

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    attempt_429 += 1
                    if attempt_429 < max_429_attempts:
                        await asyncio.sleep(backoff_429)
                        backoff_429 *= 2
                        continue
                if 500 <= exc.response.status_code < 600:
                    attempt_5xx += 1
                    if attempt_5xx < max_5xx_attempts:
                        await asyncio.sleep(backoff_5xx)
                        backoff_5xx *= 2
                        continue
                raise

    async def close(self) -> None:
        self._access_token = None
        self._token_expires_at = None
        return None
