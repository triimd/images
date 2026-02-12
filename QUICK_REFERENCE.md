# Quick Reference

## Images

1. `infra-tools`
2. `dev-node`
3. `dev-python`
4. `job-image`
5. `git-sync`
6. `git-relay`
7. `bootstrap`

## Registry Paths

```bash
<registry>/<namespace>/infra-tools
<registry>/<namespace>/dev-node
<registry>/<namespace>/dev-python
<registry>/<namespace>/job-image
<registry>/<namespace>/git-sync
<registry>/<namespace>/git-relay
<registry>/<namespace>/bootstrap
```

## Local Builds

```bash
docker build -t infra-tools:local ./infra-tools
docker build -t dev-node:local --build-arg BASE_IMAGE=infra-tools:local ./dev-node
docker build -t dev-python:local --build-arg BASE_IMAGE=infra-tools:local ./dev-python
docker build -t job-image:local ./job-image
docker build -t git-sync:local ./git-sync
docker build -t git-relay:local ./git-relay
docker build -t bootstrap:local ./bootstrap
```

## Releases

- Tag format: `<image>-v<semantic-version>`
- Example:

```bash
git tag infra-tools-v1.0.0
git push origin infra-tools-v1.0.0
```

- Generated tags: `1.0.0`, `1.0`, `1`, `latest`

## CI Workflow

- Single workflow: `.github/workflows/images.yml`
- Detects changed image directories automatically
- Manual dispatch supports `auto`, `all`, or specific image
- Uses multi-platform builds (`linux/amd64,linux/arm64`)
