FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip \
  && python -m pip install --no-cache-dir kubernetes

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app
USER 10001
WORKDIR /home/app
