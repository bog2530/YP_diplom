from typing import Any
import threading

import aiohttp


_cxt = threading.local()


def get_client() -> aiohttp.ClientSession:
    if not hasattr(_cxt, "client"):
        _cxt.client = aiohttp.ClientSession()
    return _cxt.client

async def fetch_films(url: str, params: dict[str, Any]) -> dict | None:
    async with get_client().get(url, params=params) as response:
        try:
            response.raise_for_status()
            result = await response.json()
            return result
        except aiohttp.ClientError as e:
            return None

