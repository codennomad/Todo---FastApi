from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
async def create_user(user: UserSchemas, session: Session):
    """
    Create a new user.

    Receives user data (username, email, password), hashes the password,
    stores the user in the database, and returns the created user's
    public information without exposing the password.

    Raises:
        HTTPException (409 Conflict): If the
        username or email already exists.

    Returns:
        UserPublic: The public representation of the newly created user.
    """
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
async def read_users(
    session: Session, filter_users: Annotated[FilterPage, Query()]
):
    """
    Retrieve all users.

    Returns a paginated list of users currently stored in the database.
    Supports `offset` and `limit` query parameters for pagination.

    Args:
        session (Session): The database session,
        injected by `get_session`.
        filter_users (FilterPage): Query parameters
        for pagination (offset, limit).

    Returns:
        UserList: A list of `UserPublic` objects.
    """
    result = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    users = result.all()

    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchemas,
    session: Session,
    current_user: CurrentUser,
):
    """
    Update an existing user.

    Updates the username, email, and password of the user specified
    by `user_id`. Only the authenticated user can update their own profile.

    Raises:
        HTTPException (403 Forbidden): If the authenticated
        user tries to update another user's profile.
        HTTPException (409 Conflict): If the new username
        or email already exists for another user.

    Returns:
        UserPublic: The updated user's public information.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions'
        )

    # Verifica se o novo username ou email já está em uso por outro usuário
    conflict_user = await session.scalar(
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
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    """
    Delete a user.

    Removes the user specified by `user_id` from the database.
    Only the authenticated user can delete their own profile.

    Raises:
        HTTPException (403 Forbidden): If the authenticated
        user tries to delete another user's profile.

    Returns:
        Message: A confirmation message indicating successful deletion.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
