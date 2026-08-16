from app.core.credentials.credential import Credential


class ClientIdSecretCredential(Credential):
    def __init__(self, client_id: str, client_secret: str, source: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._source = source

    def get_type(self) -> str:
        return "client_id_secret"

    def mask(self) -> str:
        if len(self._client_secret) <= 4:
            return "***"
        return self._client_secret[:4] + "***"

    def is_empty(self) -> bool:
        return not bool(self._client_id) or not bool(self._client_secret)

    def source(self) -> str:
        return self._source

    def get_client_id(self) -> str:
        return self._client_id

    def get_client_secret(self) -> str:
        return self._client_secret

    async def on_before_use(self) -> None:
        pass

    async def on_after_use(self) -> None:
        pass

    async def on_expiry(self) -> None:
        pass
