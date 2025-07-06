import logging
from typing import Any, Optional, Dict
import threading

import aiohttp

logger = logging.getLogger(__name__)

_cxt = threading.local()


def get_client() -> aiohttp.ClientSession:
    if not hasattr(_cxt, "client"):
        _cxt.client = aiohttp.ClientSession()
    return _cxt.client


async def make_request(
    method: str,
    url: str,
    params: Dict[str, Any] | None = None,
    json: Dict[str, Any] | None = None,
    data: Any | None = None,
) -> Optional[Dict[str, Any]]:
    try:
        async with get_client().request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            data=data,
        ) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"ERROR requesting {url}: {e}")
        return None
