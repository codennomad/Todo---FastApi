from http import HTTPStatus

from fastapi.testclient import TestClient

from todo_fast.app import app


def test_root():
    client = TestClient(app)

    respose = client.get('/')
    assert respose.status_code == HTTPStatus.OK
    assert respose.json() == {'message': 'Hello, World!'}
