from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from todo_fast.models import Todo, TodoState


class TodoFactory(factory.Factory):
    """
    Factory for creating test Todo instances.

    This factory uses `factory-boy` to generate
    `Todo` objects with
    random titles, descriptions, and states,
    and sets a default `user_id`
    for convenience in tests.
    """
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    """
    Test the successful creation of a new todo
    item via the API.

    This test sends a POST request to the `/todos`
    endpoint with valid
    todo data and an authorization token.
    It asserts that the response
    status code is OK and that the returned JSON
    matches the expected
    newly created todo item.

    Args:
        client (TestClient): The FastAPI test
        client fixture.
        token (str): A valid access token for
        authentication.
    """
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        }
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_list_should_return5(session, client, user, token):
    """
    Test listing todos returns the correct number of items.

    This test creates a batch of 5 todo items for a
    specific user and then
    sends a GET request to the `/todos/` endpoint.
    It asserts that the
    response contains exactly 5 todo items,
    verifying the listing functionality.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        client (TestClient): The FastAPI test client fixture.
        user (User): The user fixture for associating todos.
        token (str): A valid access token for authentication.
    """
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_pagination_should_return2(
    session, user, client, token
):
    """
    Test listing todos with pagination parameters.

    This test creates 5 todo items and then sends
    a GET request to the
    `/todos/` endpoint with `offset=1` and `limit=2` parameters. It
    asserts that the response returns exactly 2 todo items, verifying
    the pagination functionality.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture for associating todos.
        client (TestClient): The FastAPI test client fixture.
        token (str): A valid access token for authentication.
    """
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    """
    Test listing todos filtered by title.

    This test creates 5 todo items with a specific
    title and then sends
    a GET request to the `/todos/` endpoint with
    a `title` query parameter.
    It asserts that the response contains exactly
    5 todo items matching the filter.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture for
        associating todos.
        client (TestClient): The FastAPI
        test client fixture.
        token (str): A valid access token for authentication.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_filter_description_should_return5(
    session, user, client, token
):
    """
    Test listing todos filtered by description.

    This test creates 5 todo items with
    a specific description and then sends
    a GET request to the `/todos/` endpoint
    with a `description` query parameter
    (partial match). It asserts that the
    response contains exactly 5 todo items
    matching the filter.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture
        for associating todos.
        client (TestClient): The FastAPI
        test client fixture.
        token (str): A valid access token
        for authentication.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            description='description')
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return5(
    session, user, client, token
):
    """
    Test listing todos filtered by state.

    This test creates 5 todo items with a
    specific state and then sends
    a GET request to the `/todos/`
    endpoint with a `state` query parameter.
    It asserts that the response contains
    exactly 5 todo items matching the filter.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture for
        associating todos.
        client (TestClient): The FastAPI
        test client fixture.
        token (str): A valid access token
        for authentication.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filtercombined_should_return5(
    session, user, client, token
):
    """
    Test listing todos with combined filters
    (title, description, and state).

    This test creates a batch of 5 todo items
    matching specific criteria and
    another batch that doesn't.
    It then sends a GET request to the `/todos/`
    endpoint with multiple query parameters.
    It asserts that only the 5
    matching todo items are returned, verifying combined filtering.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture for
        associating todos.
        client (TestClient): The FastAPI
        test client fixture.
        token (str): A valid access token
        for authentication.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_patch_todo_error(client, token):
    """
    Test attempting to patch a non-existent todo item.

    This test sends a PATCH request to
    an ID that doesn't exist.
    It asserts that the response status
    code is `HTTPStatus.NOT_FOUND`
    and that the error detail indicates
    the task was not found.

    Args:
        client (TestClient): The FastAPI
        test client fixture.
        token (str): A valid access token
        for authentication.
    """
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    """
    Test successfully patching an existing todo item.

    This test first creates a todo item. Then,
    it sends a PATCH request
    to update its title. It asserts that
    the response status code is OK
    and that the updated title is
    reflected in the response.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        client (TestClient): The FastAPI test
        client fixture.
        user (User): The user fixture for
        associating todos.
        token (str): A valid access token
        for authentication.
    """
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token):
    """
    Test the successful deletion of an existing todo item.

    This test creates a todo item, then sends
    a DELETE request to remove it.
    It asserts that the response status code
    is OK and that the success
    message is returned.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        client (TestClient): The FastAPI test client fixture.
        user (User): The user fixture for associating todos.
        token (str): A valid access token for authentication.
    """
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_deleted_todo_error(client, token):
    """
    Test attempting to delete a non-existent todo item.

    This test sends a DELETE request for a todo item ID that does not exist.
    It asserts that the response status code is `HTTPStatus.NOT_FOUND`
    and that the error detail indicates the task was not found.

    Args:
        client (TestClient): The FastAPI test client fixture.
        token (str): A valid access token for authentication.
    """
    response = client.delete(
        f'/todos/{10}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Task not found.'
    }
