from http import HTTPStatus

from jwt import decode

from todo_fast.security import create_access_token, settings


def test_jwt():
    """
    Test the creation and decoding of a JSON Web Token (JWT).

    This test verifies that `create_access_token` correctly encodes
    data into a JWT and that `jwt.decode` can successfully decode it
    using the application's secret key and algorithm. It also asserts
    that the original data is present in the decoded token and that
    an expiration (`exp`) claim is included.
    """
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    """
    Test API behavior when an invalid JWT is provided.

    This test simulates a request to a
    protected endpoint with a malformed
    or invalid token in the `Authorization` header.
    It asserts that the
    API returns an `HTTPStatus.UNAUTHORIZED`
    response with the expected
    error detail, indicating that the token
    could not be validated.

    Args:
        client (TestClient): The FastAPI test client fixture.
    """
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
