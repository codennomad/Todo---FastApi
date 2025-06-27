from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
from jwt import encode

from todo_fast.security import settings


def test_get_token(client, user):
    """
    Test the successful retrieval of an access token.

    Verifies that a valid user's credentials
    result in a 200 OK
    response containing an access_token and token_type.

    Args:
        client (TestClient): The FastAPI test client.
        user (User): A fixture providing a
        test user object.
    """
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    """
    Test that an access token expires after its designated time.

    It simulates token generation at a specific
    time and attempts to use it
    after the expiration period, expecting an
    UNAUTHORIZED status.

    Args:
        client (TestClient): The FastAPI test client.
        user (User): A fixture providing a test user object.
    """
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_inexistent_user(client):
    """
    Test token generation for a non-existent user.

    Ensures that attempting to get a token with
    credentials for a user
    not in the database results in an UNAUTHORIZED error.

    Args:
        client (TestClient): The FastAPI test client.
    """
    response = client.post(
        '/auth/token',
        data={'username': 'no_user@no_domain.com', 'password': 'testtest'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_password(client, user):
    """
    Test token generation with an incorrect password
    for an existing user.

    Confirms that providing the wrong password
    for a valid user
    leads to an UNAUTHORIZED response.

    Args:
        client (TestClient): The FastAPI test client.
        user (User): A fixture providing a test user object.
    """
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, user, token):
    """
    Test the successful refreshing of an access token.

    Verifies that a valid token can be used to obtain a new,
    refreshed token.

    Args:
        client (TestClient): The FastAPI test client.
        user (User): A fixture providing a test user object(
            though not directly used in the refresh call,
            it's part of the test setup context
        ).
        token (str): A fixture providing a valid access token.
    """
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    """
    Test that an expired token cannot be refreshed.

    Simulates an expired token and attempts to refresh it,
    expecting an UNAUTHORIZED status.

    Args:
        client (TestClient): The FastAPI test client.
        user (User): A fixture providing a test user object.
    """
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_no_subject_in_token(client):
    """
    Test get_current_user when JWT token has no 'sub' field.

    Simulates a token that is valid but lacks the
    'sub' (subject/email) field,
    expecting a 401 UNAUTHORIZED response.

    Args:
        client (TestClient): The test client
        for the FastAPI application.
    """
    invalid_payload = {"some_other_field": "value"}
    invalid_payload.update({'exp': datetime.now(
        tz=ZoneInfo('UTC')) + timedelta(minutes=1)}
    )

    malformed_token = encode(
        invalid_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {malformed_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_non_existent_user_from_token(client):
    """
    Test get_current_user when JWT token
    'sub' refers to a non-existent user.

    Simulates a token for a user that does not exist in the database,
    expecting a 401 UNAUTHORIZED response.

    Args:
        client (TestClient): The test client
        for the FastAPI application.
    """
    non_existent_email = "non_existent@example.com"
    payload = {"sub": non_existent_email}
    payload.update({'exp': datetime.now(
        tz=ZoneInfo('UTC')) + timedelta(minutes=1)}
    )

    non_existent_user_token = encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {non_existent_user_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
