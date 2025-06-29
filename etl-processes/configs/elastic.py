from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from .base import BaseSettings


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTIC_")
    MOVIES_INDEX: str = "movies"
    GENRES_INDEX: str = "genres"
    PERSONS_INDEX: str = "persons"
    NODES: list[str] = ["http://elasticsearch:9200"]
    USERNAME: str = ""
    PASSWORD: str = ""

    @field_validator("NODES", mode="before")
    @classmethod
    def NODE_LIST(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return value.split(",")
        else:
            return value


ELASTIC = ElasticSettings()
