# Git Sync

A lightweight utility for synchronizing Git repositories at regular intervals.

## Features

- Lightweight Alpine-based image
- Automatic periodic synchronization
- Configurable sync interval
- Support for SSH and HTTPS authentication

## Environment Variables

- `SOURCE_REPO` (required): Source repository URL
- `TARGET_REPO` (required): Target repository URL
- `BRANCH` (default: `main`): Branch to sync
- `SYNC_INTERVAL` (default: `300`): Sync interval in seconds

## Usage

```bash
docker run -d \
  -e SOURCE_REPO="https://github.com/user/source-repo.git" \
  -e TARGET_REPO="https://github.com/user/target-repo.git" \
  -e BRANCH="main" \
  -e SYNC_INTERVAL="300" \
  ghcr.io/triimd/git-sync:latest
```

## With SSH Keys

```bash
docker run -d \
  -v ~/.ssh:/root/.ssh:ro \
  -e SOURCE_REPO="git@github.com:user/source-repo.git" \
  -e TARGET_REPO="git@github.com:user/target-repo.git" \
  ghcr.io/triimd/git-sync:latest
```

## Use Cases

- Mirror repositories between different Git hosting services
- Create backup copies of repositories
- Sync between private and public repositories
- Maintain repository replicas
