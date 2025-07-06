from logging import config as logging_config

from pydantic import BaseSettings, Field
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    movie_api: str = Field("movies", env="MOVIE_API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
