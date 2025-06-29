import logging
from contextlib import closing

import elastic_transport
from celery import shared_task
from configs.elastic import ELASTIC
from connector import elastic_client, postgres_connector, redis_client
from etls import (
    DataTransform,
    ElasticsearchUploader,
    PostgresExtractor,
)
from psycopg.rows import dict_row
from storage import RedisStorage, State

MOVIES_LOCK_KEY = "update_movies_index_lock"
GENRES_LOCK_KEY = "update_genres_index_lock"
PERSONS_LOCK_KEY = "update_persons_index_lock"
FILM_WORKS_LAST_CHECK_KEY = "film_works_last_check"
GENRES_LAST_CHECK_KEY = "genres_last_check"
PERSONS_LAST_CHECK_KEY = "persons_last_check"
LOCK_TIMEOUT = 15


@shared_task()
def update_movies_index():
    """Задача на обновление данных в индексе movies"""
    uploader = ElasticsearchUploader(elastic_client)
    data_transformer = DataTransform()
    state = State(RedisStorage(redis_client=redis_client, state_key="movies_sync"))

    try:
        if not elastic_client.indices.exists(index=ELASTIC.MOVIES_INDEX):
            logging.error("🚨 Movies index does not exist!")
            return
    except elastic_transport.ConnectionError:
        logging.error("🚨 Couldn't connect to elastic!")
        return

    #  Лок, чтобы не допустить наложения задач друг на друга
    if not redis_client.set(name=MOVIES_LOCK_KEY, value=1, nx=True, ex=15):
        logging.warning("Task already running. Skipping execution.")
        return

    try:
        with postgres_connector() as postgres_conn:
            with closing(postgres_conn.cursor(row_factory=dict_row)) as postgres_cursor:
                loader = PostgresExtractor(pg_cursor=postgres_cursor)
                updated_films, updated_persons, updated_genres = 0, 0, 0

                for batch in loader.extract_movies_data(from_ts=state.get_state(key=FILM_WORKS_LAST_CHECK_KEY)):
                    film_works = data_transformer.transform_movies(batch)
                    uploader.bulk_update_movies(data=film_works)
                    if film_works:
                        state.set_state(key=FILM_WORKS_LAST_CHECK_KEY, value=film_works[-1].updated_at)
                    updated_films += len(film_works)
                    redis_client.expire(MOVIES_LOCK_KEY, LOCK_TIMEOUT)

                for batch in loader.extract_genres_from_films_data(from_ts=state.get_state(key=GENRES_LAST_CHECK_KEY)):
                    film_works = data_transformer.transform_movies(batch)
                    uploader.bulk_update_movies(data=film_works)
                    if film_works:
                        state.set_state(key=GENRES_LAST_CHECK_KEY, value=film_works[-1].updated_at)
                    updated_genres += len(film_works)
                    redis_client.expire(MOVIES_LOCK_KEY, LOCK_TIMEOUT)

                for batch in loader.extract_persons_from_films_data(
                    from_ts=state.get_state(key=PERSONS_LAST_CHECK_KEY)
                ):
                    film_works = data_transformer.transform_movies(batch)
                    uploader.bulk_update_movies(data=film_works)
                    if film_works:
                        state.set_state(key=PERSONS_LAST_CHECK_KEY, value=film_works[-1].updated_at)
                    updated_persons += len(film_works)
                    redis_client.expire(MOVIES_LOCK_KEY, LOCK_TIMEOUT)

                logging.info(f"{updated_films=}, {updated_persons=}, {updated_genres=}, ")
    finally:
        redis_client.delete(MOVIES_LOCK_KEY)


@shared_task()
def update_genres_index():
    """Задача на обновление данных в индексе genres"""
    uploader = ElasticsearchUploader(elastic_client)
    data_transformer = DataTransform()
    state = State(RedisStorage(redis_client=redis_client, state_key="genres_sync"))

    try:
        if not elastic_client.indices.exists(index=ELASTIC.GENRES_INDEX):
            logging.error("🚨 Genres index does not exist!")
            return
    except elastic_transport.ConnectionError:
        logging.error("🚨 Couldn't connect to elastic!")
        return

    #  Лок, чтобы не допустить наложения задач друг на друга
    if not redis_client.set(name=GENRES_LOCK_KEY, value=1, nx=True, ex=15):
        logging.warning("Task already running. Skipping execution.")
        return

    try:
        with postgres_connector() as postgres_conn:
            with closing(postgres_conn.cursor(row_factory=dict_row)) as postgres_cursor:
                loader = PostgresExtractor(pg_cursor=postgres_cursor)
                updated_genres = 0

                for batch in loader.extract_genres_data(from_ts=state.get_state(key=GENRES_LAST_CHECK_KEY)):
                    genres = data_transformer.transform_genres(batch)
                    uploader.bulk_update_genres(data=genres)
                    if genres:
                        state.set_state(key=GENRES_LAST_CHECK_KEY, value=genres[-1].updated_at)
                    updated_genres += len(genres)
                    redis_client.expire(GENRES_LOCK_KEY, LOCK_TIMEOUT)

                logging.info(f"{updated_genres=}")
    finally:
        redis_client.delete(GENRES_LOCK_KEY)


@shared_task()
def update_persons_index():
    """Задача на обновление данных в индексе persons"""
    uploader = ElasticsearchUploader(elastic_client)
    data_transformer = DataTransform()
    state = State(RedisStorage(redis_client=redis_client, state_key="persons_sync"))

    try:
        if not elastic_client.indices.exists(index=ELASTIC.PERSONS_INDEX):
            logging.error("🚨 Persons index does not exist!")
            return
    except elastic_transport.ConnectionError:
        logging.error("🚨 Couldn't connect to elastic!")
        return

    #  Лок, чтобы не допустить наложения задач друг на друга
    if not redis_client.set(name=PERSONS_LOCK_KEY, value=1, nx=True, ex=15):
        logging.warning("Task already running. Skipping execution.")
        return

    try:
        with postgres_connector() as postgres_conn:
            with closing(postgres_conn.cursor(row_factory=dict_row)) as postgres_cursor:
                loader = PostgresExtractor(pg_cursor=postgres_cursor)
                updated_persons = 0

                for batch in loader.extract_persons_data(from_ts=state.get_state(key=PERSONS_LAST_CHECK_KEY)):
                    persons = data_transformer.transform_persons(batch)
                    uploader.bulk_update_persons(data=persons)
                    if persons:
                        state.set_state(key=PERSONS_LAST_CHECK_KEY, value=persons[-1].updated_at)
                    updated_persons += len(persons)
                    redis_client.expire(PERSONS_LOCK_KEY, LOCK_TIMEOUT)

                logging.info(f"{updated_persons=}")
    finally:
        redis_client.delete(PERSONS_LOCK_KEY)
