from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache

from models.genre import Genre
from services.genre import GenreService
from api.v1.openapi_schemas import not_found_404
from dependencies import get_genre_service

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", responses=not_found_404, response_model=list[Genre])
@cache(expire=120)
async def get_genres(
    page_size: int = Query(10, ge=1, le=100),
    page_number: int = Query(1, ge=1),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    """
    Список жанров.
    """
    genres = await genre_service.search(page_size=page_size, page_number=page_number)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")
    return genres


@router.get("/{genre_id}/", responses=not_found_404, response_model=Genre)
@cache(expire=120)
async def genre_details(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    """
    Данные по конкретному жанру.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
