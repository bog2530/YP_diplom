from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self._index = "persons"

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        return await self._get_person_from_elastic(person_id)

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index=self._index, id=str(person_id))
            return Person(**doc["_source"])
        except NotFoundError:
            return None

    async def search(self, *, page_size: int, page_number: int, search_query: str = None) -> list[Person]:
        query = {}

        if search_query:
            query["match"] = {"full_name": search_query}

        response = await self.elastic.search(
            index=self._index,
            size=page_size,
            from_=(page_number - 1) * page_size,
            query=query or {"match_all": {}},  # if query is {}
        )

        return [Person(**item["_source"]) for item in response.get("hits", {}).get("hits", [])]
