from abc import ABC, abstractmethod


class Credential(ABC):
    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def mask(self) -> str:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def source(self) -> str:
        pass

    @abstractmethod
    async def on_before_use(self) -> None:
        pass

    @abstractmethod
    async def on_after_use(self) -> None:
        pass

    @abstractmethod
    async def on_expiry(self) -> None:
        pass
