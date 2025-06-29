from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettings(BaseSettings):
    """
    Конфиг подключения к редису
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
