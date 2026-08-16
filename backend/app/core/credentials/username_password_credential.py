from app.core.credentials.credential import Credential


class UsernamePasswordCredential(Credential):
    def __init__(self, username: str, password: str, source: str) -> None:
        self._username = username
        self._password = password
        self._source = source

    def get_type(self) -> str:
        return "username_password"

    def mask(self) -> str:
        if len(self._password) <= 4:
            return "***"
        return self._password[:4] + "***"

    def is_empty(self) -> bool:
        return not bool(self._username) or not bool(self._password)

    def source(self) -> str:
        return self._source

    def get_username(self) -> str:
        return self._username

    def get_password(self) -> str:
        return self._password

    async def on_before_use(self) -> None:
        pass

    async def on_after_use(self) -> None:
        pass

    async def on_expiry(self) -> None:
        pass
