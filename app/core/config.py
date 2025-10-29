from pydantic_settings import BaseSettings
from pydantic import EmailStr, SecretStr


class Settings(BaseSettings):
    # JWT / авторизация
    SECRET_KEY: str = "secret_key"
    ACCESS_EXPIRE_MINUTES: int = 30
    REFRESH_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Email (Gmail)
    EMAIL_USERNAME: str = "ruzikofficial@gmail.com"
    EMAIL_PASSWORD: SecretStr = SecretStr("chabekiwjeojljso")  # App password
    EMAIL_FROM: EmailStr = "ruzikofficial@gmail.com"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USE_TLS: bool = True    # TLS
    EMAIL_USE_SSL: bool = False   # SSL (не нужен если TLS)
    EMAIL_USE_CREDS: bool = True  # использовать логин/пароль для SMTP

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: SecretStr = SecretStr("supersecretpassword")

    # PostgreSQL Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr("postgres")
    DB_NAME: str = "jwttest"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"        # можно хранить настройки в .env
        case_sensitive = False


settings = Settings()
