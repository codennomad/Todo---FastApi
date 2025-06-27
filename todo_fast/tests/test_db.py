from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fast.database import get_session
from todo_fast.models import Todo, User


def to_dict(obj):
    """
    Converts a SQLAlchemy model instance to a dictionary.

    This function iterates through the columns
    of the given SQLAlchemy object
    and creates a dictionary where keys are
    column names and values are
    the corresponding attribute values of the object.

    Args:
        obj (DeclarativeBase): An instance
        of a SQLAlchemy declarative model.

    Returns:
        dict: A dictionary representation of the model instance.
    """
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    """
    Test the creation and persistence of a new user in the database.

    This test verifies that a `User`
    object can be successfully added to the
    database, committed, and then retrieved,
    asserting that its attributes,
    including the `created_at` timestamp
    (mocked by `mock_db_time`),
    match the expected values.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        mock_db_time (Callable): The fixture providing
        the `_mock_db_time` context manager.
    """
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test',
            password='secret',
            email='test@test',
        )
        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'test')
        )

        assert asdict(user) == {
            'id': 1,
            'username': 'test',
            'password': 'secret',
            'email': 'test@test',
            'created_at': time,
            'todos': [],
        }


@pytest.mark.asyncio
async def test_get_session_yield():
    """
    Test the `get_session` asynchronous
    generator function.

    This test verifies that `get_session`
    correctly yields an `AsyncSession`
    object and can be properly closed,
    ensuring the dependency injection
    mechanism for database sessions
    functions as expected.
    """
    gen = get_session()
    session = await anext(gen)
    assert session is not None
    await gen.aclose()


@pytest.mark.asyncio
async def test_create_todo(session, user):
    """
    Test the creation and persistence of a
    new todo item in the database.

    This test verifies that a `Todo` object
    can be successfully added to the
    database, committed, and then retrieved,
    asserting that its attributes
    match the expected values. It also confirms
    the association with a user.

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.
        user (User): The user fixture providing a test user.
    """
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'description': 'Test Desc',
        'id': 1,
        'state': 'draft',
        'title': 'Test Todo',
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    """
    Test the one-to-many relationship between
    User and Todo models.

    This test verifies that after creating a
    `Todo` and associating it with a `User`,
    the `todos` relationship attribute of the
    `User` object correctly contains
    the newly created todo item.

    Args:
        session (AsyncSession): The
        SQLAlchemy async session fixture.
        user (User): The user fixture providing a test user.
    """
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(
        select(User).where(User.id == user.id)
    )

    assert user.todos == [todo]
