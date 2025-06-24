from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_fast.database import get_session
from todo_fast.models import User
from todo_fast.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchemas,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    GET/

    Returns a welcome message for the API root endpoint.
    """
    return {'message': 'Hello, World!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchemas, session: Session = Depends(get_session)):
    """
    Create a new user.

    Receives user data (username, email, password), assings a unique ID,
    stores it in the in-memory database, and returns the created user
    without expossing the password.
    """
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username,
        password=user.password,
        email=user.email,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """
    Retrieve all users.

    Returns a list of users currently stored in the database.
    """
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchemas, session: Session = Depends(get_session)
):
    """
    Update an existing user.

    Updates the username, email, password of the user specified
    by user_id. Raises 404 if the user does not exist.
    """
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    conflict_user = session.scalar(
        select(User).where(
            ((User.username == user.username) | (User.email == user.email)) &
            (User.id != user_id)
        )
    )

    if conflict_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    db_user.username = user.username
    db_user.password = user.password
    db_user.email = user.email
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int, session: Session = Depends(get_session)
):
    """
    Delete a user.

    Removes the user specified by user_id from the database.
    Raises 404 if the user does not exist.
    """
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}
