import os
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = "movies"

    # Настройки Redis
    REDIS_HOST: str = Field(alias="REDIS_CACHE_HOST")
    REDIS_PORT: int = Field(alias="REDIS_CACHE_PORT")

    # Настройки Elasticsearch
    ELASTIC_SCHEMA: str = Field("http")
    ELASTIC_HOST: str = Field("localhost")
    ELASTIC_PORT: int = Field(9200)

    AUTH_SERVICE_SCHEMA: str = Field("http")
    AUTH_SERVICE_HOST: str = Field("localhost")
    AUTH_SERVICE_PORT: int = Field(5005)

    JAEGER_HOST: str = Field("localhost", alias="JAEGER_HOST")
    JAEGER_PORT: int = Field(6831, alias="JAEGER_PORT")

    # Корень проекта
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @computed_field
    @property
    def AUTH_SERVICE_URI(self) -> str:
        return f"{self.AUTH_SERVICE_SCHEMA}://{self.AUTH_SERVICE_HOST}:{self.AUTH_SERVICE_PORT}"


settings = Settings()
