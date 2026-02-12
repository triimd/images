FROM python:3.13-alpine3.21

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Webhook fanout relay for git-sync services"
LABEL org.opencontainers.image.licenses=MIT

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY setup-image.sh /tmp/setup-image.sh
RUN sh /tmp/setup-image.sh && rm -f /tmp/setup-image.sh

COPY git-relay.py /app/git-relay.py
RUN chmod +x /app/git-relay.py

USER git-relay

EXPOSE 8080

CMD ["python", "/app/git-relay.py"]
