from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Интеграция Алисы для кинотеатра"
    app_description: str = (
        "Сервис для взаимодействия Rasa-bot кинотеатр и колонки Яндекс.Алиса"
    )
    rasa_url: str = "http://127.0.0.1:5005"


settings = Settings()
