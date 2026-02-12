#!/usr/bin/env sh

set -eu

addgroup -S git-relay
adduser -S -G git-relay git-relay
chown -R git-relay:git-relay /app
