from typing import Any

import aiohttp


class RasaService:
    def __init__(self, session: aiohttp.ClientSession, rasa_url: str):
        self.session = session
        self.rasa_url = rasa_url

    async def get_rasa(self, user_id: str, message: str) -> dict | None:
        data = {"sender": user_id, "message": message}

        async with self.session.post(
            f"{self.rasa_url}/webhooks/rest/webhook",
            json=data,
        ) as response:
            try:
                response.raise_for_status()
                result = await response.json()
                print(data)
                print(f"{result}")
                return result
            except aiohttp.ClientError as error:
                print(f"Error: {error}")
