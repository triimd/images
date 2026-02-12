FROM python:3.13-alpine3.21

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Webhook-driven Git mirror service"
LABEL org.opencontainers.image.licenses=MIT

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GIT_SYNC_DATA_DIR=/var/lib/git-sync \
    PORT=8080

COPY setup-image.sh /tmp/setup-image.sh
RUN sh /tmp/setup-image.sh && rm -f /tmp/setup-image.sh

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY git-sync.py /app/git-sync.py
RUN chmod +x /app/git-sync.py

USER git-sync

EXPOSE 8080

CMD ["python", "/app/git-sync.py"]
