#!/usr/bin/env bash

set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

pipx install --force poetry
poetry config virtualenvs.in-project true
