from logging import config as logging_config

from pydantic import BaseSettings, Field
from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    MOVIE_API: str = Field("movies", env="MOVIE_API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
