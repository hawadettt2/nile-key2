from .auth import router
from .shipping import router
from .invoice import router
from .suppliers import router
from .customers import router
from .customs import router
from .resources import router
from .documents import router
from .eta import router
from .digital_export_manager import router as digital_export_manager_router

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
    "digital_export_manager_router",
]
