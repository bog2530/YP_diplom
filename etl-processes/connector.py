import logging
from contextlib import contextmanager
from typing import Generator

import psycopg
import redis
from configs.elastic import ELASTIC
from configs.postgres import POSTGRES
from configs.redis import REDIS
from elasticsearch import Elasticsearch


@contextmanager
def postgres_connector() -> Generator[psycopg.Connection, None, None]:
    """Контекстный менеджер для работы с Postgres"""
    connection: psycopg.Connection = psycopg.connect(
        dbname=POSTGRES.DB,
        host=POSTGRES.HOST,
        user=POSTGRES.USERNAME,
        password=POSTGRES.PASSWORD,
        port=POSTGRES.PORT,
    )

    try:
        yield connection
    except Exception as e:
        connection.rollback()
        logging.exception(e)
    finally:
        connection.close()


redis_client = redis.Redis.from_url(
    REDIS.URI,
    encoding="utf-8",
    decode_responses=True,
    max_connections=1000,
)

elastic_client = Elasticsearch(
    hosts=ELASTIC.NODES,
    request_timeout=60,
    retry_on_timeout=True,
    max_retries=1,
    verify_certs=False,
    basic_auth=(ELASTIC.USERNAME, ELASTIC.PASSWORD),
)
