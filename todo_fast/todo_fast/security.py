from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fast.database import get_session
from todo_fast.models import User
from todo_fast.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    """
    Creates a JSON Web Token (JWT) access token.

    The token includes the provided data and an expiration timestamp
    based on the `ACCESS_TOKEN_EXPIRE_MINUTES` setting.

    Args:
        data (dict): The payload data to be encoded into the token.
                     Typically includes a 'sub' (subject) field.

    Returns:
        str: The encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encode_jwt = encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encode_jwt


def get_password_hash(password: str):
    """
    Hashes a plain-text password using the recommended
    password hashing algorithm.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """
    Verifies if a plain-text password matches a given hashed password.

    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    """
    FastAPI dependency function to get the current authenticated
    user from a JWT.

    This function extracts the token from the request, decodes it,
    validates its signature and expiration, and then fetches the corresponding
    user from the database. It raises an HTTPException if the token is invalid
    or expired, or if the user does not exist.

    Args:
        session (AsyncSession): The database session dependency.
        token (str): The JWT extracted from the Authorization
        header by `oauth2_scheme`.

    Raises:
        HTTPException (401 Unauthorized): If credentials could not be validated
                                          (e.g., invalid token, expired token,
                                          missing 'sub' claim,
                                          or user not found).

    Returns:
        User: The authenticated User model instance.
    """
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
