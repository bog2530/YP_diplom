FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app/src:$PYTHONPATH"

COPY [ \
  "pyproject.toml", \
  "uv.lock", \
"./"]
COPY src ./src

RUN uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0","--port", "8000"]
