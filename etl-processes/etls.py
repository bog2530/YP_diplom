import sqlite3
from datetime import datetime
from typing import Generator, TypeVar

import psycopg
from configs.elastic import ELASTIC
from elasticsearch import Elasticsearch, helpers
from schemas import GenresElasticsearchModel, MoviesElasticsearchModel, PersonsElasticsearchModel

T = TypeVar("T")

BATCH_SIZE = 100


class ElasticsearchUploader:
    def __init__(self, elastic_client: Elasticsearch):
        self.elastic_client = elastic_client

    def bulk_update_movies(self, data: list[MoviesElasticsearchModel]):
        helpers.bulk(
            client=self.elastic_client,
            actions=[
                {
                    "_index": ELASTIC.MOVIES_INDEX,
                    "_op_type": "update",
                    "_id": item.id,
                    "_retry_on_conflict": 1,
                    "doc_as_upsert": True,
                    "doc": item.model_dump(exclude_none=True, by_alias=True, exclude={"updated_at"}),
                }
                for item in data
            ],
        )

    def bulk_update_genres(self, data: list[GenresElasticsearchModel]):
        helpers.bulk(
            client=self.elastic_client,
            actions=[
                {
                    "_index": ELASTIC.GENRES_INDEX,
                    "_op_type": "update",
                    "_id": item.id,
                    "_retry_on_conflict": 1,
                    "doc_as_upsert": True,
                    "doc": item.model_dump(exclude_none=True, by_alias=True, exclude={"updated_at"}),
                }
                for item in data
            ],
        )

    def bulk_update_persons(self, data: list[PersonsElasticsearchModel]):
        helpers.bulk(
            client=self.elastic_client,
            actions=[
                {
                    "_index": ELASTIC.PERSONS_INDEX,
                    "_op_type": "update",
                    "_id": item.id,
                    "_retry_on_conflict": 1,
                    "doc_as_upsert": True,
                    "doc": item.model_dump(exclude_none=True, by_alias=True, exclude={"updated_at"}),
                }
                for item in data
            ],
        )


class PostgresExtractor:
    def __init__(self, pg_cursor: psycopg.Cursor):
        self.pg_cursor = pg_cursor

    def extract_movies_data(self, from_ts: datetime = None) -> Generator[list[sqlite3.Row], None, None]:
        """Метод для извлечения данных о фильмах из БД"""
        where_clause = f"WHERE fw.modified > '{from_ts}'" if from_ts else ""

        query = f"""
            SELECT
            fw.id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            fw.permissions,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'id', p.id,
                        'name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null and pfw.role = 'actor'),
                '[]'
            ) as actors,
                COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'id', p.id,
                        'name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null and pfw.role = 'writer'),
                '[]'
            ) as writers,
                COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'id', p.id,
                        'name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null and pfw.role = 'director'),
                '[]'
            ) as directors,
            array_agg(DISTINCT g.name) as genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            {where_clause}
            GROUP BY fw.id
            ORDER BY fw.modified;
        """
        self.pg_cursor.execute(query)
        while results := self.pg_cursor.fetchmany(BATCH_SIZE):
            yield results

    def extract_genres_from_films_data(self, from_ts: datetime = None) -> Generator[list[sqlite3.Row], None, None]:
        """Метод для извлечения данных о жанрах из БД"""
        where_clause = f"WHERE g.modified > '{from_ts}'" if from_ts else ""

        query = f"""
            SELECT
                fw.id,
                max(g.modified) modified,
                array_agg(DISTINCT g.name) as genres
            FROM content.genre g
            LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
            LEFT JOIN content.film_work fw ON fw.id = gfw.film_work_id
            {where_clause}
            GROUP BY fw.id
            ORDER BY max(g.modified);
        """
        self.pg_cursor.execute(query)
        while results := self.pg_cursor.fetchmany(BATCH_SIZE):
            yield results

    def extract_genres_data(self, from_ts: datetime = None) -> Generator[list[sqlite3.Row], None, None]:
        """Метод для извлечения данных о жанрах из БД"""
        where_clause = f"WHERE g.modified > '{from_ts}'" if from_ts else ""

        query = f"""
            SELECT
                g.id,
                g.name,
                max(g.modified) modified
            FROM content.genre g
            JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
            {where_clause}
            GROUP BY g.id
            ORDER BY max(g.modified);
        """
        self.pg_cursor.execute(query)
        while results := self.pg_cursor.fetchmany(BATCH_SIZE):
            yield results

    def extract_persons_from_films_data(self, from_ts: datetime = None) -> Generator[list[sqlite3.Row], None, None]:
        """Метод для извлечения данных о персонах из БД"""
        where_clause = f"WHERE pfw_sub.film_work_id = fw.id AND p_sub.modified > '{from_ts}'" if from_ts else ""
        query = f"""
            SELECT
                fw.id,
                MAX(p.modified) modified,
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'actor'),
                    '[]'
                ) AS actors,
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'writer'),
                    '[]'
                ) AS writers,
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id IS NOT NULL AND pfw.role = 'director'),
                    '[]'
                ) AS directors
            FROM content.film_work fw
            JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
            JOIN content.person p ON p.id = pfw.person_id
            WHERE EXISTS (
                SELECT 1 FROM content.person p_sub
                JOIN content.person_film_work pfw_sub ON p_sub.id = pfw_sub.person_id
                {where_clause}
            )
            GROUP BY fw.id
            ORDER BY MAX(p.modified);
        """
        self.pg_cursor.execute(query)
        while results := self.pg_cursor.fetchmany(BATCH_SIZE):
            yield results

    def extract_persons_data(self, from_ts: datetime = None) -> Generator[list[sqlite3.Row], None, None]:
        """Метод для извлечения данных о персонах из БД"""
        where_clause = f"WHERE p.modified > '{from_ts}'" if from_ts else ""

        query = f"""
            SELECT
                p.id,
                p.full_name,
                MAX(p.modified) AS modified,
                JSON_AGG(
                    JSONB_BUILD_OBJECT(
                        'id', pfw.film_work_id,
                        'roles', roles_array
                    )
                ) AS films
            FROM content.person p
            JOIN (
                SELECT
                    pfw.person_id,
                    pfw.film_work_id,
                    ARRAY_AGG(pfw.role) AS roles_array
                FROM content.person_film_work pfw
                GROUP BY pfw.person_id, pfw.film_work_id
            ) pfw ON p.id = pfw.person_id
            {where_clause}
            GROUP BY p.id
            ORDER BY MAX(p.modified);
        """
        self.pg_cursor.execute(query)
        while results := self.pg_cursor.fetchmany(BATCH_SIZE):
            yield results


class DataTransform:
    def transform_movies(self, batch):
        """Принимает список сырых данных (batch) и cписок моделей адаптированных под индекс movies"""
        return [MoviesElasticsearchModel.model_validate(item) for item in batch]

    def transform_genres(self, batch):
        """Принимает список сырых данных (batch) и cписок моделей адаптированных под индекс genres"""
        return [GenresElasticsearchModel.model_validate(item) for item in batch]

    def transform_persons(self, batch):
        """Принимает список сырых данных (batch) и cписок моделей адаптированных под индекс persons"""
        return [PersonsElasticsearchModel.model_validate(item) for item in batch]
