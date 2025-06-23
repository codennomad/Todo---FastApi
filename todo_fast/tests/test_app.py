from http import HTTPStatus


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
    assert response.json() == {
        'users': [
            {
                'username': 'alice',
                'email': 'alice@example.com',
                'id': 1,
            }
        ]
    }


def test_update_user(client):
    """
    Test the user update endpoint.

    Sends a PUT request to /users/{user_id} with updated data and
    verifies that user is updated correctly.
    """
    response = client.put(
        'users/1',
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
        'id': 1,
    }


def test_delete_user(client):
    """
    Test the user deletion endpoint.

    Ensures that DELETE /users/{user_id} sucessfully deletes the user
    and returns the appropriate sucess message.
    """
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
