# Docker Images Repository

A general-purpose repository for storing and building Docker images with automated GitHub Actions workflows. Images are published to GitHub Container Registry (ghcr.io).

## Available Images

| Image | Description | Container Registry |
|-------|-------------|-------------------|
| **ubuntu-workflow** | Ubuntu-based image for GitHub Actions, act, and Gitea workflows | `ghcr.io/triimd/ubuntu-workflow` |
| **git-sync** | Utility for synchronizing Git repositories at regular intervals | `ghcr.io/triimd/git-sync` |
| **git-relay** | Webhook relay service for Git events | `ghcr.io/triimd/git-relay` |
| **bootstrap** | Environment initialization and bootstrapping utility | `ghcr.io/triimd/bootstrap` |

## Quick Start

Pull and run an image:

```bash
# Pull an image
docker pull ghcr.io/triimd/ubuntu-workflow:latest

# Run an image
docker run -it ghcr.io/triimd/ubuntu-workflow:latest
```

## Repository Structure

```
.
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
        ├── ubuntu-workflow.yml
        ├── git-sync.yml
        ├── git-relay.yml
        └── bootstrap.yml
```

## Versioning Pattern

This repository uses a **per-image versioning** pattern to allow independent versioning of each Docker image within the same repository.

### Tag Format

Images are versioned using Git tags with the following format:

```
<image-name>-v<semantic-version>
```

**Examples:**
- `ubuntu-workflow-v1.0.0`
- `git-sync-v2.1.3`
- `bootstrap-v1.2.0`

### Automatic Tagging

When you push a tag matching the pattern above, GitHub Actions will automatically:
1. Build the corresponding image
2. Tag it with the semantic version
3. Publish it to GitHub Container Registry

### Available Tags

Each image in the registry includes the following tags:

| Tag Pattern | Description | Example |
|-------------|-------------|---------|
| `latest` | Latest build from main branch | `ghcr.io/triimd/ubuntu-workflow:latest` |
| `<version>` | Full semantic version | `ghcr.io/triimd/ubuntu-workflow:1.2.3` |
| `<major>.<minor>` | Major and minor version | `ghcr.io/triimd/ubuntu-workflow:1.2` |
| `<major>` | Major version only | `ghcr.io/triimd/ubuntu-workflow:1` |
| `<branch>-<sha>` | Branch with commit SHA | `ghcr.io/triimd/ubuntu-workflow:main-abc1234` |
| `pr-<number>` | Pull request builds | `ghcr.io/triimd/ubuntu-workflow:pr-42` |

### Versioning Workflow

#### 1. Making Changes

Make changes to a specific image directory:

```bash
cd ubuntu-workflow/
# Edit Dockerfile or other files
git add .
git commit -m "feat: add new tool to ubuntu-workflow"
git push
```

This will trigger a build that creates the `latest` tag (on main branch).

#### 2. Creating a Release

To create a versioned release:

```bash
# Create and push a tag for the specific image
git tag ubuntu-workflow-v1.2.0
git push origin ubuntu-workflow-v1.2.0
```

This will trigger a build that creates version-specific tags (1.2.0, 1.2, 1).

#### 3. Independent Versioning

Each image can be versioned independently:

```bash
# Release ubuntu-workflow v2.0.0
git tag ubuntu-workflow-v2.0.0
git push origin ubuntu-workflow-v2.0.0

# Release git-sync v1.5.0 (different version)
git tag git-sync-v1.5.0
git push origin git-sync-v1.5.0
```

### Version Bumping Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes or breaking changes
- **MINOR** version (X.Y.0): Backward-compatible new features
- **PATCH** version (X.Y.Z): Backward-compatible bug fixes

**Examples:**
- Add new tool: `ubuntu-workflow-v1.1.0` (minor)
- Fix bug in script: `git-sync-v1.0.1` (patch)
- Change environment variable names: `bootstrap-v2.0.0` (major)

## Building Images Locally

Build a specific image locally:

```bash
# Build ubuntu-workflow
docker build -t ubuntu-workflow:local ./ubuntu-workflow

# Build git-sync
docker build -t git-sync:local ./git-sync

# Build git-relay
docker build -t git-relay:local ./git-relay

# Build bootstrap
docker build -t bootstrap:local ./bootstrap
```

## Publishing to GitHub Container Registry

Images are automatically published to GitHub Container Registry when:

1. **On push to main/develop**: Creates/updates the `latest` tag
2. **On tag push**: Creates version-specific tags
3. **Manual trigger**: Via GitHub Actions `workflow_dispatch`

### Manual Publishing

You can manually trigger a build from the GitHub Actions UI:

1. Go to the "Actions" tab
2. Select the workflow for your image (e.g., "Build ubuntu-workflow")
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

### Authentication

To pull private images:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull private image
docker pull ghcr.io/triimd/ubuntu-workflow:latest
```

## CI/CD Integration

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/triimd/ubuntu-workflow:latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
```

### Docker Compose

```yaml
version: '3.8'
services:
  git-sync:
    image: ghcr.io/triimd/git-sync:latest
    environment:
      SOURCE_REPO: "https://github.com/user/source.git"
      TARGET_REPO: "https://github.com/user/target.git"
```

## Contributing

### Adding a New Image

1. Create a new directory with the image name
2. Add a `Dockerfile` and `README.md`
3. Create a workflow file in `.github/workflows/`
4. Update this README to list the new image
5. Submit a pull request

### Modifying an Existing Image

1. Make changes to the image directory
2. Update the image's README if needed
3. Test locally with `docker build`
4. Submit a pull request
5. After merge, tag a new version if releasing

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.