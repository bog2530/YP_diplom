from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from core.enums import PermissionEnum

from api.v1.openapi_schemas import not_found_404
from dependencies import FilmService, GenreService, get_film_service, get_genre_service
from security import get_permissions
from models.enums import SortOption
from models.film import Film, FilmBase

router = APIRouter(prefix="/films", tags=["films"])


@router.get("/search", responses=not_found_404, response_model=list[FilmBase])
@cache(expire=120)
async def get_films_by_title(
    title: str = Query(None, max_length=100),
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    film_service: FilmService = Depends(get_film_service),
):
    """Поиск фильма по названию"""
    films = await film_service.search(title=title, page_size=page_size, page_number=page_number)

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="films not found",
        )

    return films


@router.get("/{film_id}", responses=not_found_404, response_model=Film)
@cache(expire=120)
async def film_details(
    film_id: UUID,
    permissions: list[PermissionEnum] = Depends(get_permissions),
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    """Поиск фильма по ID"""
    film = await film_service.get_by_id(film_id)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found",
        )

    if not all(required_permission in permissions for required_permission in film.permissions):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions",
        )

    return film


@router.get("/", responses=not_found_404, response_model=list[FilmBase])
@cache(expire=120)
async def get_films(
    sort: SortOption = Query(
        None,
        description='Choose "-imdb_rating" for descending by film rating' ', "imdb_rating" for ascending',
    ),
    genre_id: Optional[UUID] = Query(None, alias="genre"),
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    film_service: FilmService = Depends(get_film_service),
    genre_service: GenreService = Depends(get_genre_service),
):
    """Получить все фильмы"""
    genre = None
    if genre_id:
        genre = await genre_service.get_by_id(genre_id)

        if not genre:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="genre not found",
            )

    films = await film_service.search(
        sort=sort,
        genres=genre and [genre.name],
        page_size=page_size,
        page_number=page_number,
    )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="films not found",
        )

    return films


@router.get("/similar/", responses=not_found_404, response_model=list[FilmBase])
@cache(expire=120)
async def get_similar(
    film_id: UUID,
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    film_service: FilmService = Depends(get_film_service),
):
    """Поиск похожих фильмов"""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found",
        )

    films = await film_service.search(
        genres=film.genres,
        page_size=page_size,
        page_number=page_number,
    )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="films not found",
        )

    return films


@router.get("/top-genre/", responses=not_found_404, response_model=list[FilmBase])
@cache(expire=120)
async def get_top_genres(
    genre_id: UUID = Query(alias="genre"),
    page_size: int = Query(50, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    film_service: FilmService = Depends(get_film_service),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[FilmBase]:
    """
    Популярные фильмы в жанре.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="genre not found",
        )

    films = await film_service.search(
        sort=SortOption.desc, genres=[genre.name], page_size=page_size, page_number=page_number
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return films
