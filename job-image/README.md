# Job Image

General-purpose Node-based runtime image for executing workload jobs.

## Features

- Based on `node:20-bookworm`
- Includes Git, SSH client, and CA certificates
- Uses non-root `node` user

## Usage

```bash
docker run -it <registry>/<namespace>/job-image:latest
```
