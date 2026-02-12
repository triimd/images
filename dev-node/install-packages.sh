#!/usr/bin/env bash

set -euo pipefail

NVM_VERSION="${NVM_VERSION:-v0.40.3}"
export NVM_DIR="${NVM_DIR:-$HOME/.local/share/nvm}"

mkdir -p "$NVM_DIR"

if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  git clone --depth=1 --branch "$NVM_VERSION" https://github.com/nvm-sh/nvm.git "$NVM_DIR"
fi

# shellcheck source=/dev/null
source "$NVM_DIR/nvm.sh"

nvm install --lts
nvm install 20
nvm install 22
nvm alias default lts/*

corepack enable

mkdir -p "$HOME/.cache/npm" "$HOME/.config/npm" "$HOME/.local/share/pnpm"
npm config set cache "$HOME/.cache/npm" --location=user
npm config set prefix "$HOME/.local" --location=user

export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$HOME/.local/bin:$PATH"

pnpm config set store-dir "$HOME/.local/share/pnpm/store"
pnpm add -g typescript-language-server vscode-langservers-extracted
