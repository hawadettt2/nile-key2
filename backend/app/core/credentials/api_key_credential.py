from app.core.credentials.credential import Credential


class ApiKeyCredential(Credential):
    def __init__(self, key: str, source: str) -> None:
        self._key = key
        self._source = source

    def get_type(self) -> str:
        return "api_key"

    def mask(self) -> str:
        if len(self._key) <= 4:
            return "***"
        return self._key[:4] + "***"

    def is_empty(self) -> bool:
        return not bool(self._key)

    def source(self) -> str:
        return self._source

    def get_key(self) -> str:
        return self._key

    async def on_before_use(self) -> None:
        pass

    async def on_after_use(self) -> None:
        pass

    async def on_expiry(self) -> None:
        pass
