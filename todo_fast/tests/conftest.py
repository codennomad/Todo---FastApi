from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from todo_fast.app import app
from todo_fast.database import get_session
from todo_fast.models import User, table_registry
from todo_fast.security import get_password_hash


class UserFactory(factory.Factory):
    """
    Factory for creating test User instances.

    This factory uses `factory-boy`
    to generate `User` objects with
    sensible defaults for testing purposes,
    including unique usernames
    and emails, and a hashed password.
    """
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest.fixture
def client(session):
    """
    Provides a FastAPI TestClient instance
    configured with a test database session.

    This fixture overrides the `get_session`
    dependency of the FastAPI application
    to use the test session, ensuring that all
    API calls during tests interact
    with the isolated test database. It yields
    the client and then clears
    the dependency override.

    Args:
        session (AsyncSession): The SQLAlchemy async session fixture.

    Yields:
        TestClient: An instance of `fastapi.testclient.TestClient`.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    """
    Provides an asynchronous SQLAlchemy engine
    connected to a temporary PostgreSQL container.

    This fixture sets up a Dockerized PostgreSQL
    database using `testcontainers-python`,
    creates an asynchronous SQLAlchemy engine
    connected to it, and ensures the
    container is properly torn down after all
    tests in the session are complete.

    Yields:
        AsyncEngine: An asynchronous SQLAlchemy engine instance.
    """
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    """
    Provides an isolated asynchronous SQLAlchemy
    session for each test.

    This fixture first creates all database tables
    defined in `table_registry.metadata`
    using the provided engine. It then yields an
    `AsyncSession` instance for the test.
    After the test completes, it drops all tables,
    ensuring a clean state for the next test.

    Args:
        engine (AsyncEngine): The asynchronous SQLAlchemy engine fixture.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session instance.
    """
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    """
    Context manager to mock the 'created_at'
    timestamp for a given SQLAlchemy model.

    During the context, it sets up an event
    listener that intercepts 'before_insert'
    events for the specified model and sets
    its `created_at` attribute to a
    predetermined `time`. This is useful
    for testing time-sensitive logic
    without relying on the system's current time.

    Args:
        model (DeclarativeBase): The SQLAlchemy model
        class to mock the time for.
        time (datetime, optional): The datetime object
        to use for `created_at`.
                                   Defaults to
                                   `datetime(2025, 1, 1)`.

    Yields:
        datetime: The mocked time that was applied.
    """
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """
    Provides the `_mock_db_time` context manager as a fixture.

    This allows tests to easily mock database timestamps by calling
    `mock_db_time()` within a `with` statement.

    Returns:
        Callable: The `_mock_db_time` context manager.
    """
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    """
    Provides a pre-created and persisted test user for tests.

    This fixture creates a `User` instance using `UserFactory`, hashes a
    known password, adds the user to the database, commits the session,
    and refreshes the user object. It also attaches the `clean_password`
    attribute for easy access during tests.

    Args:
        session (AsyncSession): The SQLAlchemy async session fixture.

    Returns:
        User: A persisted `User` object with a `clean_password` attribute.
    """
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    """
    Provides an access token for the `user` fixture.

    This fixture makes a POST request to the
    `/auth/token` endpoint
    using the credentials of the `user`
    fixture and returns the
    `access_token` from the response.

    Args:
        client (TestClient): The FastAPI test
        client fixture.
        user (User): The user fixture providing a test user.

    Returns:
        str: The access token string.
    """
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    """
    Provides a second pre-created and persisted
    test user for tests.

    Similar to the `user` fixture,
    but creates a distinct user, useful
    for testing scenarios involving multiple
    users (e.g., permissions).

    Args:
        session (AsyncSession): The SQLAlchemy
        async session fixture.

    Returns:
        User: A persisted `User` object with a
        `clean_password` attribute.
    """
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user
