from pydantic import BaseModel


class TextAlisa(BaseModel):
    text: str


class Alisa(BaseModel):
    response: TextAlisa
    version: str = "1.0"
    end_session: bool = False
