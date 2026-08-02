import os
import tempfile
import shutil

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

from main import app  # noqa: E402


@pytest.fixture(scope="function", autouse=True)
def _isolated_database():
    """Ensure each test uses an isolated temporary database."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")

    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite:///{db_path}"

    from app.core.database import init_db
    init_db()

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
