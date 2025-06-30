from typing import Optional

from pydantic import BaseModel, Field
from uuid import UUID
from core.enums import PermissionEnum


class FilmBase(BaseModel, populate_by_name=True):
    id: UUID = Field(alias="uuid")
    title: str
    imdb_rating: float


class Film(FilmBase):
    description: Optional[str] = None
    genres: list[str]
    actors: list[dict[str, str]]
    directors: list[dict[str, str]]
    writers: list[dict[str, str]]


class FilmInternal(Film):
    permissions: str
