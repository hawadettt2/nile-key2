from typing import Dict, List, Optional

from app.core.credentials.credential import Credential


class CredentialStore:
    def __init__(self) -> None:
        self._store: Dict[str, Credential] = {}

    def register(self, name: str, credential: Credential) -> None:
        self._store[name] = credential

    def get(self, name: str) -> Optional[Credential]:
        return self._store.get(name)

    def get_or_raise(self, name: str) -> Credential:
        credential = self._store.get(name)
        if credential is None:
            raise KeyError(f"Credential '{name}' not found in CredentialStore")
        return credential

    def list_sources(self) -> Dict[str, str]:
        return {name: credential.source() for name, credential in self._store.items()}

    def list_all(self) -> List[str]:
        return list(self._store.keys())
