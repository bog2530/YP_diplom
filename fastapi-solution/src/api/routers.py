from fastapi import APIRouter

from api.v1 import routers

v1_router = APIRouter(prefix="/v1")

for route in routers:
    v1_router.include_router(route)
