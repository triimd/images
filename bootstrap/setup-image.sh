#!/usr/bin/env sh

set -eu

apk add --no-cache \
  bash \
  ca-certificates \
  curl \
  gettext \
  git \
  jq \
  openssh-client \
  wget \
  yq

addgroup -S bootstrap
adduser -S -G bootstrap bootstrap

mkdir -p /workspace /config
chown -R bootstrap:bootstrap /workspace /config
