import asyncio
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api import list_of_routes
from core.config import settings

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource


# Взамен устаревших startup и shutdown
# https://fastapi.tiangolo.com/advanced/events/#alternative-events-deprecated
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    es = AsyncElasticsearch(hosts=[f"{settings.ELASTIC_SCHEMA}{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])
    await asyncio.to_thread(FastAPICache.init, RedisBackend(redis), "fastapi-cache")
    yield {"es": es, "redis": redis}
    await redis.close()
    await es.close()


def configure_tracer():
    resource = Resource.create(attributes={"service.name": "api-movies"})
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER_HOST, agent_port=settings.JAEGER_PORT, udp_split_oversized_batches=True
    )

    trace_provider = TracerProvider(resource=resource, sampler=TraceIdRatioBased(1.0))

    trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(trace_provider)


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

configure_tracer()
FastAPIInstrumentor.instrument_app(app)


# @app.middleware("http")
# async def request_id_middleware(request: Request, call_next):
#     request_id = request.headers.get("X-Request-Id")
#     if not request_id:
#         return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
#
#     tracer = trace.get_tracer(__name__)
#     with tracer.start_as_current_span("http_request") as span:
#         span.set_attribute("http.request_id", request_id)
#
#         response = await call_next(request)
#
#         response.headers["X-Request-Id"] = request_id
#
#         span.set_attribute("http.status_code", response.status_code)
#
#         return response


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
def bind_routes(application: FastAPI) -> None:
    for route in list_of_routes:
        application.include_router(route, prefix="/api")


bind_routes(app)
