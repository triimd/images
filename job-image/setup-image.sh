#!/usr/bin/env bash

set -euo pipefail

apt-get update
apt-get install -y --no-install-recommends \
  bash \
  ca-certificates \
  git \
  openssh-client
rm -rf /var/lib/apt/lists/*

mkdir -p /workspace
chown -R node:node /workspace
