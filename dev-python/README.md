# Dev Python

Python development image built on top of `infra-tools`.

## Features

- Uses `pipx` to install Poetry in the user toolchain
- Configures Poetry to create in-project virtual environments
- Includes zsh/tmux/XDG dev-shell defaults for interactive development
- Reuses the shared workflow tooling from `infra-tools`

## Build Arguments

- `BASE_IMAGE` (default: `infra-tools:latest`)
- `IMAGE_SOURCE_URL` (default: `https://code.example.com/triimd/images`)
- `USERNAME` (default: `dev`)
- `USER_UID` (default: `1000`)
- `USER_GID` (default: `1000`)
- `WORKSPACE_DIR` (default: `/workspace`)

## Usage

```bash
docker run -it <registry>/<namespace>/dev-python:latest
```

## Local Build

```bash
docker build -t dev-python:local --build-arg BASE_IMAGE=infra-tools:local ./dev-python
```
