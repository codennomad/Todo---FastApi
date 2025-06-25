from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fast.database import get_session
from todo_fast.models import User


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
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
        }


@pytest.mark.asyncio
async def test_get_session_yield():
    """"""
    gen = get_session()
    session = await anext(gen)
    assert session is not None
    await gen.aclose()
