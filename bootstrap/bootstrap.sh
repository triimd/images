#!/usr/bin/env bash

set -euo pipefail

echo "Bootstrap starting..."

if [ -f "/config/bootstrap.sh" ]; then
  echo "Running custom bootstrap configuration..."
  # shellcheck source=/dev/null
  source /config/bootstrap.sh
fi

if [ "$#" -gt 0 ]; then
  echo "Executing: $*"
  exec "$@"
fi

echo "Bootstrap complete. No additional commands to execute."
