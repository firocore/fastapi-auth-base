import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import URL


from dotenv import load_dotenv
import os
from sqlalchemy.engine.url import URL

# Загрузка переменных окружения из .env файла
load_dotenv()


class Security:
    """
    Класс для хранения настроек безопасности приложения.

    Attributes:
        SECRET_KEY (str): Секретный ключ для создания и проверки токенов.
        ALGORITHM (str): Алгоритм для создания и проверки JWT токенов.
        BACKEND_CORS_ORIGINS (list): Список разрешенных источников для CORS.
        ALLOWED_HOSTS (list): Список разрешенных хостов.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Время истечения токена доступа в минутах.
        REFRESH_TOKEN_EXPIRE_DAYS (int): Время истечения токена обновления в днях.
    """
    SECRET_KEY = os.getenv("SECURITY_SECRET_KEY", "SECRET")
    ALGORITHM = os.getenv("SECURITY_ALGORITHM", "HS256")
    BACKEND_CORS_ORIGINS = os.getenv("SECURITY_BACKEND_CORS_ORIGINS", ["http://localhost:8000"])
    ALLOWED_HOSTS = os.getenv("SECURITY_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("SECURITY_REFRESH_TOKEN_EXPIRE_DAYS", 30))


class Database:
    """
    Класс для хранения настроек подключения к базе данных.

    Attributes:
        HOSTNAME (str): Хост базы данных.
        USERNAME (str): Имя пользователя для подключения к базе данных.
        PASSWORD (str): Пароль для подключения к базе данных.
        PORT (int): Порт для подключения к базе данных.
        DB (str): Имя базы данных.
    """
    HOSTNAME = os.getenv("DATABASE_HOST", "localhost")
    USERNAME = os.getenv("DATABASE_USER", "postgres")
    PASSWORD = os.getenv("DATABASE_PASS", "postgres")
    PORT = int(os.getenv("DATABASE_PORT", 5432))
    DB = os.getenv("DATABASE_DB", "postgres")


class Settings:
    """
    Класс для хранения всех настроек приложения.

    Attributes:
        database (Database): Экземпляр класса Database для настроек базы данных.
        security (Security): Экземпляр класса Security для настроек безопасности.
    """
    def __init__(self) -> None:
        self.database = Database()  # Инициализация настроек базы данных
        self.security = Security()  # Инициализация настроек безопасности

    @property
    def database_url(self) -> URL:
        """
        Формирует URL для подключения к базе данных.

        Returns:
            URL: URL для подключения к базе данных.
        """
        return URL.create(
            drivername="postgresql+asyncpg",  # Используемый драйвер
            username=self.database.USERNAME,
            password=self.database.PASSWORD,
            host=self.database.HOSTNAME,
            port=self.database.PORT,
            database=self.database.DB,
        )


# Создание экземпляра настроек
settings = Settings()

