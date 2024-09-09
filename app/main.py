from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup!")
    yield
    logger.info("Application shutdown!")


app = FastAPI(
    title="FastAPI Auth Base",
    summary="summary",
    description="description",
    root_path="/v1",
    redoc_url=None,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
