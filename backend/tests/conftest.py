import os
import tempfile

os.environ["LIFE_USE_FIXTURES"] = "true"
os.environ["APP_ENV"] = "test"
os.environ["LIFE_TEST_AUTH_TOKEN"] = "life-test-token"
os.environ["LIFE_INTERNAL_TOKEN"] = "internal-test-token"
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/life_platform_test.db"

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
