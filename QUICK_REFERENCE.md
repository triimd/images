# Quick Reference

## Repository Overview

This repository contains 4 Docker images with automated GitHub Actions workflows:

1. **ubuntu-workflow** - Ubuntu 22.04 for CI/CD workflows
2. **git-sync** - Alpine-based git repository synchronization utility
3. **git-relay** - Node.js webhook relay service
4. **bootstrap** - Alpine-based environment initialization utility

## Quick Commands

### Pull Images
```bash
docker pull ghcr.io/triimd/ubuntu-workflow:latest
docker pull ghcr.io/triimd/git-sync:latest
docker pull ghcr.io/triimd/git-relay:latest
docker pull ghcr.io/triimd/bootstrap:latest
```

### Build Images Locally
```bash
docker build -t ubuntu-workflow:local ./ubuntu-workflow
docker build -t git-sync:local ./git-sync
docker build -t git-relay:local ./git-relay
docker build -t bootstrap:local ./bootstrap
```

### Create a Version Release
```bash
# Tag format: <image-name>-v<version>
git tag ubuntu-workflow-v1.0.0
git push origin ubuntu-workflow-v1.0.0

# This will automatically:
# 1. Trigger the workflow
# 2. Build the image
# 3. Create tags: 1.0.0, 1.0, 1, latest
# 4. Push to ghcr.io/triimd/ubuntu-workflow
```

## Versioning Pattern

Each image is versioned independently using Git tags:

- Format: `<image-name>-v<semantic-version>`
- Example: `git-sync-v2.1.3`
- Results in image tags: `2.1.3`, `2.1`, `2`, `latest`

## Workflow Triggers

Each image workflow is triggered by:
1. **Push to main/develop** with changes in image directory
2. **Version tags** (e.g., `ubuntu-workflow-v1.0.0`)
3. **Pull requests** with changes in image directory
4. **Manual dispatch** from GitHub Actions UI

## Directory Structure

```
images/
├── ubuntu-workflow/
│   ├── Dockerfile
│   └── README.md
├── git-sync/
│   ├── Dockerfile
│   └── README.md
├── git-relay/
│   ├── Dockerfile
│   └── README.md
├── bootstrap/
│   ├── Dockerfile
│   └── README.md
└── .github/
    └── workflows/
        ├── build-image.yml       # Reusable workflow
        ├── ubuntu-workflow.yml   # ubuntu-workflow build
        ├── git-sync.yml          # git-sync build
        ├── git-relay.yml         # git-relay build
        └── bootstrap.yml         # bootstrap build
```

## Adding a New Image

1. Create directory: `mkdir new-image`
2. Add `Dockerfile` and `README.md`
3. Create workflow: `.github/workflows/new-image.yml`
4. Copy workflow structure from existing image workflows
5. Update main `README.md`
6. Commit and push
7. Tag first version: `git tag new-image-v1.0.0`

## Environment Variables

### git-sync
- `SOURCE_REPO` (required)
- `TARGET_REPO` (required)
- `BRANCH` (default: main)
- `SYNC_INTERVAL` (default: 300)

### git-relay
- `PORT` (default: 8080)
- `RELAY_URL` (optional)

## Security

- All images use official base images
- No credentials embedded
- Images published to ghcr.io require GitHub token
- Workflows use GitHub's OIDC for authentication

## Support

For issues or questions, open an issue on GitHub.
