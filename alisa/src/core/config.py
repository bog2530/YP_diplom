from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Интеграция Алисы для кинотеатра"
    APP_DESCRIPTION: str = (
        "Сервис для взаимодействия Rasa-bot кинотеатр и колонки Яндекс.Алиса"
    )
    RASA_URL: str = "http://127.0.0.1:5005"


settings = Settings()
