from pydantic_settings import SettingsConfigDict

from .base import BaseSettings


class PostgresSettings(BaseSettings):
    """
    Конфиг подключения к постгресу
    """

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str = "postgres"
    PORT: str = "5432"
    USERNAME: str = "app"
    PASSWORD: str = "123qwe"
    DB: str = "movies_database"


POSTGRES = PostgresSettings()
