from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from api.v1.openapi_schemas import not_found_404
from models.film import FilmBase
from models.person import Person
from models.enums import SortOption
from dependencies import PersonService, FilmService, get_film_service, get_person_service

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/search", response_model=list[Person], responses=not_found_404, response_model_exclude_none=True)
@cache(expire=120)
async def search_persons(
    search_query: Optional[str] = Query(None, alias="query", max_length=100),
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    persons = await person_service.search(search_query=search_query, page_size=page_size, page_number=page_number)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")
    return persons


@router.get("/{person_id}", response_model=Person, responses=not_found_404)
@cache(expire=120)
async def person_details(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get("/{person_id}/film", response_model=list[FilmBase], responses=not_found_404)
@cache(expire=120)
async def get_person_films(
    person_id: UUID,
    sort: Optional[SortOption] = Query(SortOption.desc, description='Example: "-imdb_rating"'),
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    film_service: FilmService = Depends(get_film_service),
    person_service: PersonService = Depends(get_person_service),
) -> list[FilmBase]:
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    person_films = [film.id for film in person.films]

    films = await film_service.search(
        films_ids=person_films,
        page_size=page_size,
        page_number=page_number,
        sort=sort,
    )

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return films
