from dataclasses import asdict

from sqlalchemy import select

from todo_fast.database import get_session
from todo_fast.models import User


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice',
            password='secret',
            email='test@test'
        )
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'alice'))

        assert asdict(user) == {
            'id': 1,
            'username': 'alice',
            'password': 'secret',
            'email': 'test@test',
            'created_at': time,
        }


def test_get_session_yield():
    """"""
    gen = get_session()
    session = next(gen)
    assert session is not None
    gen.close()
