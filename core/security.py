from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from starlette import status

from core.config import settings
from core.database import user_collection

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


# Create hash password
def hash_password(password) -> str:
    return password_context.hash(password)


# Verify hashed password
def verify_password(plain_password, hashed_password) -> bool:
    return password_context.verify(plain_password, hashed_password)


async def create_jwt_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired, please login again!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        user = await user_collection.find_one({"email": email})
        if user is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise expired_token_exception
    except InvalidTokenError:
        raise credentials_exception

    return user


async def check_candidate_role(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(token)
    if user['role'] != 'candidate':
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")


async def check_employer_role(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(token)
    if user['role'] != 'employer':
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    return user
