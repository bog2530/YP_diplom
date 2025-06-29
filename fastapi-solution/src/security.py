import aiohttp
from fastapi import Depends
from fastapi.security import HTTPBearer


from core.config import settings
from core.enums import PermissionEnum

security = HTTPBearer()


async def get_permissions(security: str = Depends(security)) -> list[PermissionEnum]:
    """Запрос в auth-service для получения списка пермишенов пользователя"""
    async with aiohttp.ClientSession(base_url=settings.AUTH_SERVICE_URI) as session:
        async with session.get(
            "/auth-api/users/current/check-permissions",
            headers={"Authorization": security.scheme + " " + security.credentials},
        ) as response:
            return await response.json()
