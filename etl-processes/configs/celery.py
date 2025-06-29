from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    timezone: str = "Europe/Moscow"
    task_default_queue: str = "default"
    broker_connection_retry_on_startup: bool = False
    broker_pool_limit: int = 0
    worker_prefetch_multiplier: int = 1
    result_expires: int = 24 * 60 * 60
    accept_content: list[str] = ["application/json", "application/x-python-serialize"]


CELERY = CelerySettings()
