import os
import tempfile
import shutil

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

from main import app  # noqa: E402


def _register_and_approve(client: TestClient, credentials: dict, role: str = "customer") -> None:
    client.post("/api/v1/auth/register", json=credentials)
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    import sqlite3
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (credentials["email"],))
    row = cursor.fetchone()
    user_id = row[0] if row else None
    conn.close()
    if user_id:
        client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})


@pytest.fixture(scope="function", autouse=True)
def _isolated_database():
    """Ensure each test uses an isolated temporary database."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")

    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite:///{db_path}"

    from app.core.database import init_db
    init_db()

    os.environ["DISABLE_CSRF"] = "true"
    os.environ["SEARCH_STUB_FALLBACK"] = "true"

    # Disable rate limiting for tests to avoid cross-test state leakage.
    if hasattr(app.state, "limiter") and app.state.limiter is not None:
        app.state.limiter.enabled = False

    yield

    settings.DATABASE_URL = original_db_url
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def client(_isolated_database):
    with TestClient(app) as test_client:
        yield test_client
