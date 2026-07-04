import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_smoke.db")

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_app_imports_successfully():
    assert app is not None
    assert app.title == "Nile Key API"


EXPECTED_PATH_PREFIXES = [
    "/api/v1/auth",
    "/api/v1/suppliers",
    "/api/v1/customers",
    "/api/v1/invoices",
    "/api/v1/shipping",
    "/api/v1/documents",
    "/api/v1/resources",
    "/api/v1/customs",
]


def test_all_routers_registered():
    registered_paths = [route.path for route in app.routes if hasattr(route, "path")]
    missing = [prefix for prefix in EXPECTED_PATH_PREFIXES if not any(path.startswith(prefix) for path in registered_paths)]
    assert not missing, f"Missing router prefixes: {missing}"


def test_root_endpoint_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
