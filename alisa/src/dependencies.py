from functools import lru_cache

import aiohttp
from fastapi import Depends
from starlette.requests import Request

from services.rasa import RasaService
from core import settings


async def get_aiohttp(request: Request) -> aiohttp.ClientSession:
    return request.app.state.aiohttp_session


@lru_cache()
def get_rasa_service(
    session: aiohttp.ClientSession = Depends(get_aiohttp),
) -> RasaService:
    return RasaService(session, settings.rasa_url)
