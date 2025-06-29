from uuid import UUID
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

from models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self._index = "genres"

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        return await self._get_genre_from_elastic(genre_id)

    async def _get_genre_from_elastic(self, genre_id: UUID) -> Optional[Genre]:
        try:
            response = await self.elastic.get(
                index=self._index,
                id=str(genre_id),
            )
            result = Genre(**response["_source"])
        except NotFoundError:
            return None
        return result

    async def search(self, *, page_size: int, page_number: int) -> list[Genre]:
        body = {
            "query": {"match_all": {}},
            "sort": [{"name.raw": {"order": "asc"}}],
        }
        response = await self.elastic.search(
            index=self._index,
            size=page_size,
            from_=(page_number - 1) * page_size,
            body=body,
        )
        return [Genre(**item["_source"]) for item in response.get("hits", {}).get("hits", [])]
