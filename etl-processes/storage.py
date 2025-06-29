import abc
import json
from datetime import datetime
from typing import Any, Dict

from redis import Redis


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class RedisStorage(BaseStorage):
    """Реализация хранилища, использующего redis."""

    def __init__(self, redis_client: Redis, state_key: str) -> None:
        self.redis_client = redis_client
        self.state_key = state_key

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        self.redis_client.set(name=self.state_key, value=json.dumps(state))

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        state_json = self.redis_client.get(self.state_key)
        return state_json and json.loads(state_json) or {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: datetime) -> None:
        """Установить состояние для определённого ключа."""
        state = self.storage.retrieve_state()
        state[key] = value.isoformat()
        self.storage.save_state(state)

    def get_state(self, key: str) -> datetime | None:
        """Получить состояние по определённому ключу."""
        state = self.storage.retrieve_state().get(key, None)
        if state:
            return datetime.fromisoformat(state)
