from uuid import UUID

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    id: UUID = Field(alias="uuid")
    full_name: str = Field(...)


class PersonFilm(BaseModel):
    id: UUID = Field(..., alias="uuid")
    roles: list[str] = Field(default_factory=list)


class Person(PersonBase):
    films: list[PersonFilm] = Field(default_factory=list)
