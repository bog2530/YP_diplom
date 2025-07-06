import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from api.films import search_genre, top_genre, similar, get_film_data

logger = logging.getLogger(__name__)


class ActionAskFilmAuthor(Action):
    def name(self) -> Text:
        return "action_ask_film_author"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        film = tracker.get_slot("film")
        logger.info(f"Полученный слот 'film': {film}")

        film_data = await get_film_data(film)

        if not film_data:
            dispatcher.utter_message(text=f"Фильм '{film}' не найден.")
            return []

        directors = film_data.get("directors", [])
        logger.info(f"Режиссёры: {directors}")

        if isinstance(directors, list) and directors and isinstance(directors[0], dict):
            directors = ", ".join(d.get("name", "неизвестен") for d in directors)
        elif isinstance(directors, list):
            directors = ", ".join(directors)
        else:
            directors = "неизвестен"

        dispatcher.utter_message(text=f"Режиссёр фильма '{film}' — {directors}.")
        return []


class ActionAskFilmInfo(Action):
    def name(self) -> Text:
        return "action_ask_film_info"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        film = tracker.get_slot("film")
        logger.info(f"Полученный слот 'film': {film}")

        film_data = await get_film_data(film)

        if not film_data:
            dispatcher.utter_message(text=f"Фильм '{film}' не найден.")
            return []

        description = film_data.get("description", "Описание недоступно.")
        dispatcher.utter_message(text=f"{film} — {description}")
        return []


class ActionRecommendByGenre(Action):
    def name(self) -> Text:
        return "action_recommend_by_genre"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        genre_name = tracker.get_slot("genre")
        logger.info(f"Полученный слот 'genre': {genre_name}")

        if not genre_name:
            dispatcher.utter_message(text="Пожалуйста, укажи жанр.")
            return []

        genre = await search_genre(genre_name)
        logger.info(f"Информация о жанре: {genre}")

        if not genre:
            dispatcher.utter_message(text=f"Жанр '{genre_name}' не найден.")
            return []

        genre_id = genre.get("uuid")
        films = await top_genre(genre_id)
        logger.info(f"Топ фильмов по жанру '{genre_name}': {films}")

        if not films:
            dispatcher.utter_message(text=f"Нет рекомендаций по жанру '{genre_name}'.")
            return []

        film_titles = [f.get("title", "Без названия") for f in films]
        dispatcher.utter_message(
            text=f"Рекомендованные фильмы в жанре '{genre_name}': {', '.join(film_titles)}."
        )
        return []


class ActionSimilarFilms(Action):
    def name(self) -> Text:
        return "action_similar_films"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        film = tracker.get_slot("film")
        logger.info(f"Полученный слот 'film': {film}")

        film_data = await get_film_data(film)

        if not film_data:
            dispatcher.utter_message(text=f"Фильм '{film}' не найден.")
            return []

        similar_films = await similar(film_data["uuid"])
        logger.info(f"Похожие фильмы: {similar_films}")

        if not similar_films:
            dispatcher.utter_message(text=f"Похожих фильмов для '{film}' не найдено.")
            return []

        film_titles = [f.get("title", "Без названия") for f in similar_films]
        dispatcher.utter_message(
            text=f"Фильмы, похожие на '{film['title']}': {', '.join(film_titles)}."
        )
        return []
