from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from starlette.requests import Request

from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService


async def get_elastic(request: Request) -> AsyncElasticsearch:
    return request.state.es


async def get_redis(request: Request) -> Redis:
    return request.state.redis


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)


@lru_cache
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
