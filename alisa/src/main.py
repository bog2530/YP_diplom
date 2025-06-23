from contextlib import asynccontextmanager

from aiohttp import ClientSession
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import list_route
from core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    aiohttp_session = ClientSession()
    app.state.aiohttp_session = aiohttp_session
    yield
    await aiohttp_session.close()


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    openapi_url="/docs/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

for i in list_route:
    app.include_router(i)
