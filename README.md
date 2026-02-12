# Docker Images Repository

This repository stores all maintained container images used by the development and runtime stack. It replaces the legacy `dev-containers` split and keeps build/publish logic in one workflow.

The legacy `base-debian` image is intentionally retired; `infra-tools` is the shared workflow tooling base moving forward.

## Available Images

| Image | Purpose | Registry |
|-------|---------|----------|
| `infra-tools` | Ubuntu base for workflow tooling and CI containers | `<registry>/<namespace>/infra-tools` |
| `dev-node` | Node.js development image built on `infra-tools` | `<registry>/<namespace>/dev-node` |
| `dev-python` | Python development image with Poetry built on `infra-tools` | `<registry>/<namespace>/dev-python` |
| `job-image` | Lightweight Node-based runtime image for jobs | `<registry>/<namespace>/job-image` |
| `git-sync` | Webhook-driven bare-mirror sync service | `<registry>/<namespace>/git-sync` |
| `git-relay` | Webhook fanout service for `git-sync` instances | `<registry>/<namespace>/git-relay` |
| `bootstrap` | Bootstrap utility image for initialization flows | `<registry>/<namespace>/bootstrap` |

## Build and Release Workflow

Builds are handled by a single workflow: `.github/workflows/images.yml`.

- Automatically discovers changed image directories on push/PR
- Supports manual dispatch (`auto`, `all`, or a specific image)
- Uses multi-arch builds (`linux/amd64`, `linux/arm64`)
- Publishes to the configured container registry on non-PR runs

### Version Tags

Per-image releases use this tag format:

```text
<image-name>-v<semantic-version>
```

Example:

```bash
git tag git-sync-v1.2.0
git push origin git-sync-v1.2.0
```

For release tags, the workflow publishes:

- `<major>.<minor>.<patch>`
- `<major>.<minor>`
- `<major>`
- `latest`

## Build Locally

```bash
docker build -t infra-tools:local ./infra-tools
docker build -t dev-node:local --build-arg BASE_IMAGE=infra-tools:local ./dev-node
docker build -t dev-python:local --build-arg BASE_IMAGE=infra-tools:local ./dev-python
docker build -t job-image:local ./job-image
docker build -t git-sync:local ./git-sync
docker build -t git-relay:local ./git-relay
docker build -t bootstrap:local ./bootstrap
```

## Repository Structure

```text
.
├── infra-tools/
├── dev-node/
├── dev-python/
├── job-image/
├── git-sync/
├── git-relay/
├── bootstrap/
└── .github/workflows/images.yml
```

## Contributing

### Add a new image

1. Create a new image directory with `Dockerfile` and `README.md`
2. Add the image name to the image list in `.github/workflows/images.yml`
3. Update `README.md` and `QUICK_REFERENCE.md`
4. Open a PR

### Update an existing image

1. Modify files inside that image directory
2. Build locally with `docker build`
3. Open a PR
4. Tag a release when ready (`<image>-v<semver>`)

## License

MIT License - see `LICENSE`.
