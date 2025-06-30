from uuid import UUID

from api.base import make_request
from core.config import settings


# URL = settings.MOVIE_API
URL = "http://localhost:5290"


async def search_films(title: str = None, genres: UUID = None) -> dict | None:
    url = f"{URL}/api/v1/films/search"
    params = {"page_size": 1}
    if title:
        params["title"] = title
    if genres:
        params["genres"] = genres
    return await make_request("GET", url, params=params)


async def film_by_id(uuid: str) -> dict | None:
    url = f"{URL}/api/v1/films/{uuid}"
    return await make_request("GET", url)


async def search_genre(title: str) -> dict | None:
    url = f"{URL}/api/v1/genres"
    params = {"title": title, "page_size": 1}
    return await make_request("GET", url, params=params)


async def top_genre(genres: UUID) -> dict | None:
    url = f"{URL}/api/v1/films/top-genre/"
    params = {"genres": genres, "page_size": 3}
    return await make_request("GET", url, params=params)


async def similar(film_uuid: UUID) -> dict | None:
    url = f"{URL}/api/v1/films/similar/"
    params = {"film_id": film_uuid, "page_size": 3}
    return await make_request("GET", url, params=params)
