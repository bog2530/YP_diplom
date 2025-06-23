import aiohttp


class SpeechKitService:
    def __init__(self, session: aiohttp.ClientSession, rasa_url: str):
        self.session = session
        self.rasa_url = rasa_url

    async def get_speech_kit(self, user_id: str, message: str) -> str: ...
