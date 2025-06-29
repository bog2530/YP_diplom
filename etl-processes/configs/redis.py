from pydantic import computed_field
from pydantic_settings import SettingsConfigDict

from .base import BaseSettings


class RedisSettings(BaseSettings):
    """
    Конфиг подключения к редису
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_BACKEND_")

    HOST: str = "redis-backend"
    PORT: str = "6379"
    USERNAME: str = ""
    PASSWORD: str = ""
    DB: str = "1"

    @computed_field
    @property
    def URI(self) -> str:
        return f"redis://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


REDIS = RedisSettings()
