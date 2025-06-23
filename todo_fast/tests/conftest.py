import pytest
from fastapi.testclient import TestClient

from todo_fast.app import app


@pytest.fixture
def client():
    """
    Test client fixture.

    Provides a reusable TestClient instance for making requests
    to the FastApi app durint tests.
    """
    return TestClient(app)
