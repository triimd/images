# Bootstrap

A utility image for initializing and bootstrapping environments.

## Features

- Lightweight Alpine-based image
- Common initialization tools included
- Customizable bootstrap scripts
- Environment variable substitution support

## Included Tools

- bash, curl, wget
- git, openssh-client
- jq (JSON processor)
- yq (YAML processor)
- envsubst (environment variable substitution)

## Usage

### Basic Usage

```bash
docker run ghcr.io/triimd/bootstrap:latest echo "Hello from bootstrap"
```

### With Custom Bootstrap Script

```bash
docker run -v ./bootstrap.sh:/config/bootstrap.sh \
  ghcr.io/triimd/bootstrap:latest
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
git clone https://github.com/example/repo.git /workspace/repo

echo "Bootstrap complete!"
```

## Use Cases

- Environment initialization in containers
- Configuration file generation
- Repository and artifact setup
- Multi-stage build initialization
