from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
from uuid import UUID

from models.film import FilmBase, FilmInternal


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self._index = "movies"

    async def get_by_id(self, film_id: UUID) -> Optional[FilmInternal]:
        return await self._get_film_from_elastic(film_id)

    async def _get_film_from_elastic(self, film_id: UUID) -> Optional[FilmInternal]:
        try:
            doc = await self.elastic.get(index=self._index, id=str(film_id))
        except NotFoundError:
            return None
        return FilmInternal(**doc["_source"])

    async def search(
        self,
        *,
        sort: Optional[str] = None,
        title: Optional[str] = None,
        genres: list[str] = None,
        films_ids: list[UUID] = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[FilmBase]:
        query = {
            "bool": {
                "must": [],
                "filter": [],
            }
        }

        if genres:
            query["bool"]["filter"].append({"terms": {"genres": genres}})

        if films_ids:
            query["bool"]["must"].append({"terms": {"id": films_ids}})

        if title:
            query["bool"]["must"].append({"match": {"title": title}})

        es_sort = []
        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            es_sort.append({field: {"order": order}})

        response = await self.elastic.search(
            index=self._index,
            query=query or {"match_all": {}},  # if query is {}
            size=page_size,
            sort=es_sort,
            from_=(page_number - 1) * page_size,
        )

        return [FilmBase(**item["_source"]) for item in response.get("hits", {}).get("hits", [])]
