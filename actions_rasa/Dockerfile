FROM python:3.10-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app/src:$PYTHONPATH"

COPY [ \
  "pyproject.toml", \
  "uv.lock", \
"./"]
COPY src .

RUN uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "rasa", "run", "actions"]
