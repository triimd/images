#!/usr/bin/env sh

set -eu

apk add --no-cache \
  ca-certificates \
  git \
  openssh-client

addgroup -S git-sync
adduser -S -G git-sync git-sync

mkdir -p /var/lib/git-sync /app
chown -R git-sync:git-sync /var/lib/git-sync /app
