from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionAskFilmAuthor(Action):
    def name(self) -> Text:
        return "action_ask_film_author"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        film = tracker.get_slot("film")
        if film:
            authors = {
                "Начало": "Кристофер Нолан",
                "Матрица": "Братья Вачовски",
                "Престиж": "Кристофер Нолан",
                "Интерстеллар": "Кристофер Нолан"
            }
            author = authors.get(film, "неизвестен")
            dispatcher.utter_message(text=f"Режиссёр фильма '{film}' — {author}.")
        else:
            dispatcher.utter_message(text="Пожалуйста, укажи название фильма.")
        return []

class ActionAskFilmInfo(Action):
    def name(self) -> Text:
        return "action_ask_film_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        film = tracker.get_slot("film")
        if film:
            infos = {
                "Начало": "Фильм 'Начало' — это научно-фантастический триллер о снах.",
                "Матрица": "Матрица — культовый фильм о виртуальной реальности.",
                "Престиж": "Престиж — драма о соперничестве двух фокусников.",
                "Интерстеллар": "Интерстеллар — эпический научно-фантастический фильм о космосе."
            }
            info = infos.get(film, "Информация о фильме отсутствует.")
            dispatcher.utter_message(text=info)
        else:
            dispatcher.utter_message(text="Пожалуйста, укажи название фильма.")
        return []

class ActionRecommendByGenre(Action):
    def name(self) -> Text:
        return "action_recommend_by_genre"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre")
        if genre:
            recommendations = {
                "фантастика": ["Интерстеллар", "Начало", "Матрица"],
                "драма": ["Престиж", "Одержимость", "Социальная сеть"],
                "комедия": ["Суперперцы", "Очень плохие мамочки", "Клик"]
            }
            films = recommendations.get(genre.lower(), [])
            if films:
                films_list = ", ".join(films)
                dispatcher.utter_message(text=f"Рекомендую фильмы в жанре {genre}: {films_list}.")
            else:
                dispatcher.utter_message(text=f"Извините, я не знаю фильмов в жанре {genre}.")
        else:
            dispatcher.utter_message(text="Пожалуйста, укажи жанр.")
        return []

class ActionSimilarFilms(Action):
    def name(self) -> Text:
        return "action_similar_films"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        film = tracker.get_slot("film")
        if film:
            similars = {
                "Начало": ["Матрица", "Интерстеллар"],
                "Матрица": ["Начало", "Престиж"],
                "Престиж": ["Начало", "Социальная сеть"],
                "Интерстеллар": ["Начало", "Марсианин"]
            }
            similar_films = similars.get(film, [])
            if similar_films:
                films_list = ", ".join(similar_films)
                dispatcher.utter_message(text=f"Фильмы, похожие на {film}: {films_list}.")
            else:
                dispatcher.utter_message(text=f"Похожих фильмов для {film} не найдено.")
        else:
            dispatcher.utter_message(text="Пожалуйста, укажи название фильма.")
        return []
