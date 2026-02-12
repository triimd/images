# Git Relay

Webhook fanout service used by the storage layer. It receives Git webhooks and forwards events to
registered `git-sync` instances.

## Features

- Dynamic endpoint registry (`/register`, `/unregister`) with TTL pruning
- Optional static endpoint list for fixed targets
- Signature validation support for incoming webhooks
- Payload size limits and detailed fanout result reporting

## Environment Variables

- `PORT` (default: `8080`): HTTP port
- `STATIC_ENDPOINTS` (optional): Comma-separated `git-sync` endpoints
- `RELAY_FANOUT_TIMEOUT_SECONDS` (default: `5`): Timeout per fanout request
- `RELAY_ENDPOINT_TTL_SECONDS` (default: `120`): TTL for dynamically registered endpoints
- `MAX_PAYLOAD_BYTES` (default: `1048576`): Maximum accepted webhook payload size
- `WEBHOOK_SECRET` (optional): HMAC secret for webhook signature validation
- `REGISTRATION_TOKEN` (optional): Token required on register/unregister calls (`X-Relay-Token`)

## Endpoints

- `POST /register`: Register a `git-sync` endpoint (`{"endpoint":"http://..."}`)
- `POST /unregister`: Remove a `git-sync` endpoint
- `GET /endpoints`: List effective relay targets
- `POST /webhook`: Relay incoming webhook payload to all endpoints
- `GET /health`: Service health and endpoint count

## Usage

```bash
docker run -d \
  -p 8080:8080 \
  -e STATIC_ENDPOINTS="http://git-sync-a:8080,http://git-sync-b:8080" \
  -e WEBHOOK_SECRET="change-me" \
  <registry>/<namespace>/git-relay:latest
```
