from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fast.database import get_session
from todo_fast.models import User
from todo_fast.schemas import Token
from todo_fast.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2Form, session: Session):
    """
    Authenticates a user with their email and
    password and returns an access token.

    This endpoint takes an OAuth2 password flow form,
    verifies the provided
    credentials against the database,
    and if successful, issues a JWT access token.

    Raises:
        HTTPException (401 Unauthorized): If the email
        or password is incorrect.

    Returns:
        Token: An object containing the generated
        `access_token` and `token_type`.
    """
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: CurrentUser):
    """
    Refreshes an existing valid access token.

    This endpoint uses the currently
    authenticated user (obtained from the
    existing token) to issue a new access token,
    effectively extending the
    session without requiring the user to re-enter credentials.

    Args:
        user (CurrentUser): The currently authenticated user,
        injected by `get_current_user` dependency.

    Returns:
        Token: An object containing the new
        `access_token` and `token_type`.
    """
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
