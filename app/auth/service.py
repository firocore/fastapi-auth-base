from datetime import timezone, timedelta, datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from fastapi import Response, HTTPException, status

from app.core import settings
from app.auth import schemas as auth_schemas
from app.users import schemas as users_schemas
from app.users import service as users_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authorization(form_data: auth_schemas.UserAuth, response: Response, session: AsyncSession) -> auth_schemas.Token:
    async with session.begin():
        user = await users_service.get_user_by_username(form_data.username, session)

        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password!")
        
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password!")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)

        return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)

async def registration(form_data: users_schemas.UserCreate, response: Response, session: AsyncSession) -> auth_schemas.Token: 
    async with session.begin():
        new_user = await users_service.create_user(form_data, session)

        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)
        
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)

        return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)


def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES)

    token_payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        token_payload, 
        settings.security.SECRET_KEY, 
        algorithm=settings.security.ALGORITHM
    )

def create_refresh_token(user_id: int):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.security.REFRESH_TOKEN_EXPIRE_DAYS)

    token_payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        token_payload, 
        settings.security.SECRET_KEY, 
        algorithm=settings.security.ALGORITHM
    )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)