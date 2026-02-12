# Git Sync

Webhook-driven mirror service used by the storage layer. It listens for repository events, keeps
local bare mirrors in sync, archives deleted repositories, and optionally self-registers with
`git-relay`.

## Features

- Mirrors repositories as bare clones (`git clone --mirror` + fetch updates)
- Archives deleted repositories with timestamped folders
- Persists sync state and structured JSON logs on disk
- Optional registration loop with `git-relay` for dynamic fanout

## Environment Variables

- `GITEA_URL` (default: `https://git.tm0.app`): Base URL used to clone repositories
- `GIT_SYNC_DATA_DIR` (default: `/var/lib/git-sync`): Root path for mirrors/state/logs
- `SERVICE_ID` (default: `git-sync`): Service identifier
- `NODE_NAME` (default: `unknown`): Node identifier for health/registration
- `SYNC_TIMEOUT_SECONDS` (default: `120`): Timeout for each Git command
- `ARCHIVE_RETENTION_DAYS` (default: `90`): Archive cleanup retention period
- `PORT` (default: `8080`): HTTP port
- `RELAY_URL` (optional): `git-relay` base URL, enables registration loop
- `SELF_ENDPOINT` (optional): Public endpoint of this instance (for registration)
- `REGISTER_INTERVAL_SECONDS` (default: `30`): Relay registration heartbeat interval
- `RELAY_REGISTRATION_TOKEN` (optional): Token sent as `X-Relay-Token` during registration

## Endpoints

- `POST /sync`: Accepts webhook payload and performs sync/archive actions
- `GET /health`: Health and counters
- `GET /repos`: Current in-memory repository status map
- `GET /logs?lines=100`: Recent structured log records

## Usage

```bash
docker run -d \
  -p 8080:8080 \
  -e GITEA_URL="https://git.tm0.app" \
  -v git-sync-data:/var/lib/git-sync \
  <registry>/<namespace>/git-sync:latest
```
