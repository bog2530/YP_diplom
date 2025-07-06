import logging
from typing import Optional, Any, Dict, List
from uuid import UUID

from api.base import make_request
from core.config import settings

logger = logging.getLogger(__name__)


URL = settings.movie_api


async def search_films(
    title: str = None, genres: UUID = None
) -> Optional[List[Dict[str, Any]]]:
    url = f"{URL}/api/v1/films/search"
    params = {"page_size": 1}
    if title:
        params["title"] = title
    if genres:
        params["genres"] = genres
    return await make_request("GET", url, params=params)


async def film_by_id(uuid: str) -> Optional[Dict[str, Any]]:
    url = f"{URL}/api/v1/films/{uuid}"
    return await make_request("GET", url)


async def search_genre(title: str) -> Optional[list[Dict[str, Any]]]:
    url = f"{URL}/api/v1/genres"
    params = {"title": title, "page_size": 1}
    return await make_request("GET", url, params=params)


async def top_genre(genres: UUID) -> Optional[list[Dict[str, Any]]]:
    url = f"{URL}/api/v1/films/top-genre/"
    params = {"genres": genres, "page_size": 3}
    return await make_request("GET", url, params=params)


async def similar(film_uuid: UUID) -> Optional[list[Dict[str, Any]]]:
    url = f"{URL}/api/v1/films/similar/"
    params = {"film_id": film_uuid, "page_size": 3}
    return await make_request("GET", url, params=params)


async def get_film_data(title: str) -> Optional[Dict[str, Any]]:
    films = await search_films(title=title)
    if not films:
        logger.warning(f"Фильм '{title}' не найден.")
        return None

    film_id = films[0].get("uuid")
    film_data = await film_by_id(film_id)
    if not film_data:
        logger.warning(f"Не удалось получить данные по uuid фильма: {film_id}")
        return None

    return film_data
