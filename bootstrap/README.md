# Bootstrap

A utility image for initializing and bootstrapping environments.

## Features

- Lightweight Alpine-based image
- Runs as a non-root `bootstrap` user by default
- Customizable bootstrap scripts loaded from `/config/bootstrap.sh`
- Includes `envsubst` via `gettext` package

## Included Tools

- bash, curl, wget
- git, openssh-client
- jq (JSON processor)
- yq (YAML processor)
- envsubst (environment variable substitution)

## Usage

### Basic Usage

```bash
docker run <registry>/<namespace>/bootstrap:latest echo "Hello from bootstrap"
```

### With Custom Bootstrap Script

```bash
docker run -v ./bootstrap.sh:/config/bootstrap.sh \
  <registry>/<namespace>/bootstrap:latest
```

### Example Bootstrap Script

```bash
#!/bin/bash
# /config/bootstrap.sh

echo "Initializing environment..."

# Download configuration
curl -o /workspace/config.yml https://example.com/config.yml

# Process environment variables
envsubst < /workspace/config.yml > /workspace/config.processed.yml

# Clone repositories
git clone https://git.example.com/example/repo.git /workspace/repo

echo "Bootstrap complete!"
```

## Use Cases

- Environment initialization in containers
- Configuration file generation
- Repository and artifact setup
- Multi-stage build initialization
