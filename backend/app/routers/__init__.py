from .auth import router
from .shipping import router
from .invoice import router
from .suppliers import router
from .customers import router
from .customs import router
from .resources import router
from .documents import router
from .eta import router

__all__ = [
    "auth",
    "shipping",
    "invoice",
    "suppliers",
    "customers",
    "customs",
    "resources",
    "documents",
    "eta",
]
