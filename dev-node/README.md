# Dev Node

Node.js development image built on top of `infra-tools`.

## Features

- Uses `nvm` (pinned tag) for runtime management
- Preinstalls Node.js `lts`, `20`, and `22`
- Enables `corepack` and configures npm/pnpm to XDG-friendly locations
- Includes zsh/tmux/XDG dev-shell defaults for interactive development
- Includes global language server packages for JavaScript/TypeScript workflows

## Build Arguments

- `BASE_IMAGE` (default: `infra-tools:latest`)
- `IMAGE_SOURCE_URL` (default: `https://code.example.com/triimd/images`)
- `USERNAME` (default: `dev`)
- `USER_UID` (default: `1000`)
- `USER_GID` (default: `1000`)
- `WORKSPACE_DIR` (default: `/workspace`)

## Usage

```bash
docker run -it <registry>/<namespace>/dev-node:latest
```

## Local Build

```bash
docker build -t dev-node:local --build-arg BASE_IMAGE=infra-tools:local ./dev-node
```
