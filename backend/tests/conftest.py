import os
import tempfile

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-characters-abc123")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from main import app  # noqa: E402


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client
