FROM python:3.11-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'example.settings'

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        python3-dev \
        dos2unix \
        postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt --no-cache-dir

COPY run_uwsgi.sh run_uwsgi.sh
COPY uwsgi/uwsgi.ini uwsgi.ini
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod a+x /docker-entrypoint.sh && dos2unix /docker-entrypoint.sh

RUN mkdir -p /var/www/static/ \
    && mkdir -p /var/www/media/ \
    && mkdir -p /opt/app/static/ \
    && mkdir -p /opt/app/media/

COPY . .

RUN ls -l /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]