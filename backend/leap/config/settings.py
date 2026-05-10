from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Postgres
    POSTGRES_CONNECTION_STRING: str

    # App
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_WORKER_TIMEOUT: int = 120

    SEED_ON_STARTUP: bool = True

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
