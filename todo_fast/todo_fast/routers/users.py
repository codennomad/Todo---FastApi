from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_fast.database import get_session
from todo_fast.models import User
from todo_fast.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchemas,
)
from todo_fast.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
def create_user(user: UserSchemas, session: Session):
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

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
def read_users(
    session: Session, filter_users: Annotated[FilterPage, Query()]
):
    """
    Retrieve all users.

    Returns a list of users currently stored in the database.
    """
    users = session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
        ).all()

    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchemas,
    session: Session,
    current_user: CurrentUser,
):
    """
    Update an existing user.

    Updates the username, email, password of the user specified
    by user_id. Raises 404 if the user does not exist.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions'
        )

    # Verifica se o novo username ou email já está em uso por outro usuário
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

    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    current_user.email = user.email
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """
    Delete a user.

    Removes the user specified by user_id from the database.
    Raises 404 if the user does not exist.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
