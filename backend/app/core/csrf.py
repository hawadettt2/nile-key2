from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
import os


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = settings.ALLOWED_ORIGINS
        self.protected_methods = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request, call_next):
        if request.method not in self.protected_methods:
            return await call_next(request)

        if not self.allowed_origins:
            return await call_next(request)

        if os.environ.get("DISABLE_CSRF") == "true":
            return await call_next(request)

        has_cookies = bool(request.cookies)
        auth_header = request.headers.get("authorization", "")

        if not has_cookies or auth_header.strip():
            return await call_next(request)

        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        if origin:
            if origin not in self.allowed_origins:
                return JSONResponse(status_code=403, content={"detail": "CSRF origin not allowed"})
        elif referer:
            if not any(referer.startswith(o) for o in self.allowed_origins):
                return JSONResponse(status_code=403, content={"detail": "CSRF referer not allowed"})
        else:
            return JSONResponse(status_code=403, content={"detail": "CSRF token missing"})

        return await call_next(request)
