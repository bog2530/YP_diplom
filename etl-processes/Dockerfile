FROM python:3.11-slim

WORKDIR /opt/app


RUN  apt-get update -y \
     && apt-get upgrade -y \
     && apt-get install -y --no-install-recommends gcc g++ libpq-dev python3-dev \
     && apt-get clean

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir --upgrade

COPY . .
