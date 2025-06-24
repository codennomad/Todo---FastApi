from http import HTTPStatus

from todo_fast.schemas import UserPublic


def test_root(client):
    """
    Test the root endpoint.

    Ensures that GET/ returns a 200 OK status with the expected
    welcome message.
    """
    respose = client.get('/')

    assert respose.status_code == HTTPStatus.OK
    assert respose.json() == {'message': 'Hello, World!'}


def test_create_user(client):
    """
    Test user creation endpoint.

    Sends a POST request to /users/ with user data and verifies
    that the response contains the created user with an assigned ID
    and correct information.
    """
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_read_users(client):
    """
    Test the user listing endpoint.

    Ensures that GET /users/ returns a list of users with
    corresponding details.
    """
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    """
   Test the user update endpoint (PUT /users/{user_id}).

    Sends a PUT request with updated user
    data for an existing user and verifies that:
    - The response status code is 200 OK.
    - The response JSON reflects the updated user's data.
    """
    response = client.put(
        f'users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


def test_update_integrity_error(client, user, token):
    """
    Test user update with an integrity error (duplicate username/email).

    Verifies that attempting to update a user with a username or email
    that already exists triggers a 409 CONFLICT error
    with the expected detail message.
    """
    # Cria outro usuário para gerar conflito
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Tenta atualizar o usuário existente para o username já usado
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'secret',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already exists'
    }


def test_delete_user(client, user, token):
    """
    Test the user deletion endpoint (DELETE /users/{user_id}).

    Ensures that deleting an existing user returns a 200 OK status
    and the appropriate success message.
    """
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_create_user_email_conflict(client):
    """
    Test for duplicate email conflict during user creation.

    Attempts to create two users with the same email and verifies that
    the second attempt returns a 409 CONFLICT status and the specific
    'Email already exists' message.
    """
    client.post('/users/', json={
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    })

    response = client.post('/users/', json={
        'username': 'anotheruser',
        'email': 'alice@example.com',  # mesmo email
        'password': 'anothersecret',
    })

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_create_user_username_conflict(client):
    """
    Test for duplicate username conflict during user creation.

    Attempts to create two users with the same username and verifies that
    the second attempt returns a 409 CONFLICT status and the specific
    'Username already exists' message.
    """
    client.post('/users/', json={
        'username': 'charlie',
        'email': 'charlie@example.com',
        'password': 'password123',
    })

    response = client.post('/users/', json={
        'username': 'charlie',  # mesmo username
        'email': 'charlie2@example.com',
        'password': 'password456',
    })

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_update_user_not_found(client, user, token):
    """
    Test updating a non-existent user.

    Sends a PUT request to update a user with a non-existent ID and
    verifies that a 404 NOT FOUND status is returned with the
    'User not found' message.
    """
    response = client.put(
        '/users/9999',
        headers={'Authorization': f'Bearer {token}'},
        json={
        'username': 'ghost',
        'email': 'ghost@example.com',
        'password': 'void',
    })

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_not_found(client, user, token):
    """
    Test deleting a non-existent user.

    Sends a DELETE request for a user with a non-existent ID and
    verifies that a 404 NOT FOUND status is returned with the
    'User not found' message.
    """
    response = client.delete(
        '/users/9999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
