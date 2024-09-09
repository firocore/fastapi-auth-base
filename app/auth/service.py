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


# Авторизация пользователя
# Эта функция принимает данные аутентификации пользователя, проверяет их корректность и выдает токены доступа и обновления.
async def authorization(form_data: auth_schemas.UserAuth, response: Response, session: AsyncSession) -> auth_schemas.Token:
    """
    Авторизует пользователя на основе предоставленных учетных данных.

    Args:
        form_data (auth_schemas.UserAuth): Данные аутентификации (имя пользователя и пароль).
        response (Response): Ответ, в который записываются токены как cookie.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        auth_schemas.Token: Токены доступа и обновления для авторизованного пользователя.

    Raises:
        HTTPException: Если имя пользователя или пароль неверны.
    """
    async with session.begin():
        # Ищем пользователя по имени пользователя
        user = await users_service.get_user_by_username(form_data.username, session)

        # Если пользователь не найден или пароль неверный, выбрасываем исключение
        if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password!")

        # Создаем токены доступа и обновления
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        # Устанавливаем токены в cookies
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)

        return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)


# Регистрация пользователя
# Эта функция создает нового пользователя и выдает токены доступа и обновления.
async def registration(form_data: users_schemas.UserCreate, response: Response, session: AsyncSession) -> auth_schemas.Token:
    """
    Регистрирует нового пользователя и выдает токены.

    Args:
        form_data (users_schemas.UserCreate): Данные для создания нового пользователя.
        response (Response): Ответ, в который записываются токены как cookie.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        auth_schemas.Token: Токены доступа и обновления для нового пользователя.
    """
    async with session.begin():
        # Создаем нового пользователя
        new_user = await users_service.create_user(form_data, session)

        # Создаем токены доступа и обновления
        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)
        
        # Устанавливаем токены в cookies
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)

        return auth_schemas.Token(access_token=access_token, refresh_token=refresh_token)


# Создание токена доступа
def create_access_token(user_id: int) -> str:
    """
    Создает токен доступа с определенным временем истечения.

    Args:
        user_id (int): Идентификатор пользователя, для которого создается токен.

    Returns:
        str: Токен доступа, закодированный с помощью JWT.
    """
    # Получаем текушее время и дату окончания токена
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Данные токена, включающие идентификатор пользователя и время истечения
    token_payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        token_payload, 
        settings.security.SECRET_KEY, 
        algorithm=settings.security.ALGORITHM
    )


# Создание токена обновления
def create_refresh_token(user_id: int) -> str:
    """
    Создает токен обновления с длительным временем истечения.

    Args:
        user_id (int): Идентификатор пользователя, для которого создается токен.

    Returns:
        str: Токен обновления, закодированный с помощью JWT.
    """
    # Получаем текушее время и дату окончания токена
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


# Декодирование JWT токена
def decode_jwt_token(token: str) -> dict:
    """
    Декодирует JWT токен и проверяет его корректность.

    Args:
        token (str): JWT токен для декодирования.

    Returns:
        dict: Декодированные данные токена.

    Raises:
        HTTPException: Если токен недействителен или истек.
    """
    try:
        # Получем содержимое токена
        data = jwt.decode(token, settings.security.SECRET_KEY, algorithms=settings.security.ALGORITHM)
        user_id = int(data.get("sub", None))  # Получаем ID пользователя из токена
        
        return data

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сравнивает введенный пользователем пароль с захешированным.

    Args:
        plain_password (str): Пароль, введенный пользователем.
        hashed_password (str): Захешированный пароль, сохраненный в базе данных.

    Returns:
        bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Хеширование пароля
def get_password_hash(password: str) -> str:
    """
    Захеширует пароль для безопасного хранения.

    Args:
        password (str): Пароль пользователя.

    Returns:
        str: Захешированный пароль.
    """
    return pwd_context.hash(password)
