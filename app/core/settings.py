import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import URL


load_dotenv()



class Security:
    SECRET_KEY = os.getenv("SECURITY_SECRET_KEY", "SECRET")
    ALGORITHM = os.getenv("SECURITY_ALGORITHM", "HS256")
    BACKEND_CORS_ORIGINS = os.getenv("SECURITY_BACKEND_CORS_ORIGINS", ["http://localhost:8000"])
    ALLOWED_HOSTS = os.getenv("SECURITY_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("SECURITY_REFRESH_TOKEN_EXPIRE_DAYS", 30))


class Database:
    HOSTNAME = os.getenv("DATABASE_HOST", "localhost")
    USERNAME = os.getenv("DATABASE_USER", "postgres")
    PASSWORD = os.getenv("DATABASE_PASS", "postgres")
    PORT = int(os.getenv("DATABASE_PORT", 5432))
    DB = os.getenv("DATABASE_DB", "postgres")


class Settings:
    def __init__(self) -> None:
        self.database = Database()
        self.security = Security()

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.database.USERNAME,
            password=self.database.PASSWORD,
            host=self.database.HOSTNAME,
            port=self.database.PORT,
            database=self.database.DB,
        )


settings = Settings()
