import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.uncomtrade_client import UnComtradeApiClient


class TestUnComtradeApiClient:
    """Verify UN Comtrade API client behavior."""

    def test_request_builds_url_from_base_and_path(self):
        client = UnComtradeApiClient(base_url="https://comtradeapi.un.org")

        async def fake_request(method, url, params):
            assert url == "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
            return {"dataset": []}

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock, side_effect=fake_request):
            result = asyncio.run(client.request("GET", "/public/v1/preview/C/A/HS", params={"flowCode": "X"}))
        assert "dataset" in result

    def test_missing_path_raises_value_error(self):
        client = UnComtradeApiClient(base_url="https://comtradeapi.un.org")

        with pytest.raises(ValueError):
            asyncio.run(client.request("GET", "", params={}))

    def test_headers_include_api_key_when_configured(self):
        client = UnComtradeApiClient(
            base_url="https://comtradeapi.un.org",
            api_key="test-key",
        )
        headers = client._headers()
        assert headers["Accept"] == "application/json"
        assert headers["Ocp-Apim-Subscription-Key"] == "test-key"

    def test_headers_omit_api_key_when_not_configured(self):
        client = UnComtradeApiClient(base_url="https://comtradeapi.un.org")
        headers = client._headers()
        assert "Ocp-Apim-Subscription-Key" not in headers
