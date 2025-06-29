from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class PermissionEnum(StrEnum):
    READ: str = "READ"
    CREATE: str = "CREATE"
    UPDATE: str = "UPDATE"
    DELETE: str = "DELETE"


class PersonModel(BaseModel):
    id: UUID = Field(..., description="ID персоны в БД")
    name: str = Field(..., description="Имя персоны")


class MoviesElasticsearchModel(BaseModel):
    id: UUID = Field(..., description="ID кинопроизведения")

    rating: float | None = Field(None, description="Рейтинг", serialization_alias="imdb_rating")

    genres: list[str] | None = Field(None, description="Список жанров")
    actors: list[PersonModel] | None = Field(None, description="Список актеров в фильме")
    directors: list[PersonModel] | None = Field(None, description="Список директоров в фильме")
    writers: list[PersonModel] | None = Field(None, description="Список сценаристов в фильме")
    permissions: PermissionEnum | None = Field(None, description="Список требуемых пермишенов на фильм")

    title: str | None = Field(None, description="Название фильма")
    description: str | None = Field(None, description="Описание фильма")
    directors_names: list[str] | None = Field(None, description="Список имен директоров")
    actors_names: list[str] | None = Field(None, description="Список имен актеров")
    writers_names: list[str] | None = Field(None, description="Список имен сценаристов")

    updated_at: datetime = Field(description="Дата обновления", validation_alias="modified")

    @model_validator(mode="after")
    def validate_names(self) -> Self:
        self.directors_names = self.directors and [director.name for director in self.directors]
        self.writers_names = self.writers and [writers.name for writers in self.writers]
        self.actors_names = self.actors and [actors.name for actors in self.actors]
        return self


class GenresElasticsearchModel(BaseModel):
    id: UUID = Field(..., description="ID жанра", serialization_alias="uuid")
    name: str = Field(..., description="Название жанра")

    updated_at: datetime = Field(description="Дата обновления", validation_alias="modified")


class PersonsFilmsModel(BaseModel):
    id: UUID = Field(..., description="ID фильма", serialization_alias="uuid")
    roles: list[str] = Field(..., description="Список ролей в фильме")


class PersonsElasticsearchModel(BaseModel):
    id: UUID = Field(..., description="ID жанра", serialization_alias="uuid")
    full_name: str = Field(..., description="Название фильма")
    films: list[PersonsFilmsModel] = Field([], description="Список фильмов персоны")

    updated_at: datetime = Field(description="Дата обновления", validation_alias="modified")
