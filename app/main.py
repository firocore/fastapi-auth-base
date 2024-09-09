from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router



# Жизненный цикл приложения (старт и завершение)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер, который управляет жизненным циклом приложения.

    Args:
        app (FastAPI): Приложение FastAPI.

    Yields:
        None: Выполняется при запуске и завершении приложения.
    """
    logger.info("Application startup!")  # Логирование при запуске приложения
    yield  # Приложение работает здесь
    logger.info("Application shutdown!")  # Логирование при завершении приложения


# Создание экземпляра приложения FastAPI с кастомными параметрами
app = FastAPI(
    title="FastAPI Auth Base",  # Название приложения
    summary="summary",  # Краткое описание
    description="description",  # Полное описание приложения
    root_path="/v1",  # Корневой путь для всех маршрутов API
    redoc_url=None,  # Отключение документации ReDoc
    lifespan=lifespan  # Указание контекстного менеджера для управления жизненным циклом
)


# Настройка CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.BACKEND_CORS_ORIGINS,  # Разрешенные источники
    allow_credentials=True,  # Разрешение отправки cookies и заголовков
    allow_methods=["GET", "POST", "DELETE", "PUT"],  # Разрешенные HTTP методы
    allow_headers=["*"],  # Разрешенные заголовки
)


# Подключение роутеров для маршрутов авторизации и пользователей
app.include_router(auth_router)  # Роутер для авторизации
app.include_router(users_router)  # Роутер для работы с пользователями
