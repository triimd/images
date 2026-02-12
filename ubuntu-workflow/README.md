# Ubuntu Workflow

Ubuntu-based image designed for GitHub Actions workflows, act (local GitHub Actions), and Gitea Actions.

## Features

- Based on Ubuntu 22.04 LTS
- Includes common CI/CD tools:
  - Git
  - curl, wget
  - jq for JSON processing
  - Build essentials
  - Docker CLI (for Docker-in-Docker scenarios)
  - Compression tools (zip, tar, gzip)

## Usage

```bash
docker pull ghcr.io/triimd/ubuntu-workflow:latest
docker run -it ghcr.io/triimd/ubuntu-workflow:latest
```

## Use Cases

- GitHub Actions custom workflows
- Local testing with [act](https://github.com/nektos/act)
- Gitea Actions runners
- General CI/CD pipelines

## Example in GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/triimd/ubuntu-workflow:latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Your workflow steps here
```
