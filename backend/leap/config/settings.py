from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_CONNECTION_STRING: str

    JWT_SECRET_KEY: str
    JWT_EXPIRE_HOURS: int = 24
    EVENT_CODE: str

    ADMIN_API_KEY: str

    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_WORKER_TIMEOUT: int = 120

    SEED_ON_STARTUP: bool = True

    WIKI_BACK_BUTTON_ENABLED: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
