# Git Relay

A webhook relay service for Git events, useful for forwarding webhook payloads between systems.

## Features

- Lightweight Node.js-based service
- Simple HTTP webhook endpoint
- Configurable relay destination
- Health check endpoint

## Environment Variables

- `PORT` (default: `8080`): Port to listen on
- `RELAY_URL` (optional): URL to forward webhooks to

## Usage

```bash
docker run -d \
  -p 8080:8080 \
  -e RELAY_URL="https://your-service.com/webhook" \
  ghcr.io/triimd/git-relay:latest
```

## Endpoints

- `POST /webhook` - Receives webhook payloads and relays them
- `GET /health` - Health check endpoint

## Example Request

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "push", "repository": "example/repo"}'
```

## Use Cases

- Forward GitHub webhooks to internal services
- Relay webhooks across network boundaries
- Log and inspect webhook payloads
- Bridge between different webhook formats
