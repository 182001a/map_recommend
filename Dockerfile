# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# 必要ライブラリ（psycopg2用）
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /code/
