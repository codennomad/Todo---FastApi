from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from todo_fast.settings import settings

engine = create_async_engine(settings.DATABASE_URL)


async def get_session():
    """
    Dependency function to provide an asynchronous SQLAlchemy session.

    This asynchronous generator function creates an `AsyncSession`
    connected to the database defined in `settings.DATABASE_URL`.
    It yields the session for use in FastAPI dependency injection and
    ensures the session is properly closed after the request is processed,
    regardless of whether the transaction commits or rolls back.

    The `expire_on_commit=False` setting prevents objects from being
    expired after commit, which can be useful in certain scenarios
    where objects need to be accessed after a commit without re-querying.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session instance.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
