from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.users import schemas as users_schemas
from app.users import models as users_models
from app.auth import service as auth_service


async def create_user(form_data: users_schemas.UserCreate, session: AsyncSession):
    if await get_user_by_username(form_data.username, session) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists!")

    new_user = users_models.Users(
        **form_data.model_dump(exclude={"password"}), 
        hashed_password=auth_service.get_password_hash(form_data.password)
        )
    session.add(new_user)

    await session.flush()

    return new_user
    
async def get_user_by_username(username: str, session: AsyncSession):
    statement = select(users_models.Users).where(users_models.Users.username == username)
    result = await session.execute(statement)
    return result.scalars().first()
