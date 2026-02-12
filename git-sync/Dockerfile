# Git sync utility image
# Synchronizes git repositories at regular intervals

FROM alpine:3.19

LABEL org.opencontainers.image.source=https://github.com/triimd/images
LABEL org.opencontainers.image.description="Git sync utility for synchronizing repositories"
LABEL org.opencontainers.image.licenses=MIT

# Install git and required tools
RUN apk add --no-cache \
    git \
    openssh-client \
    bash \
    curl

# Create sync script
COPY <<'EOF' /usr/local/bin/git-sync
#!/bin/bash
set -e

SOURCE_REPO="${SOURCE_REPO:-}"
TARGET_REPO="${TARGET_REPO:-}"
SYNC_INTERVAL="${SYNC_INTERVAL:-300}"
BRANCH="${BRANCH:-main}"

if [ -z "$SOURCE_REPO" ] || [ -z "$TARGET_REPO" ]; then
    echo "ERROR: SOURCE_REPO and TARGET_REPO environment variables must be set"
    exit 1
fi

echo "Git Sync started"
echo "Source: $SOURCE_REPO"
echo "Target: $TARGET_REPO"
echo "Branch: $BRANCH"
echo "Interval: ${SYNC_INTERVAL}s"

while true; do
    echo "$(date): Starting sync..."
    
    # Clone or update source
    if [ ! -d /tmp/source ]; then
        git clone "$SOURCE_REPO" /tmp/source
    else
        cd /tmp/source && git fetch origin && git reset --hard origin/$BRANCH
    fi
    
    # Push to target
    cd /tmp/source
    git remote add target "$TARGET_REPO" 2>/dev/null || git remote set-url target "$TARGET_REPO"
    git push target "$BRANCH" --force
    
    echo "$(date): Sync completed"
    sleep "$SYNC_INTERVAL"
done
EOF

RUN chmod +x /usr/local/bin/git-sync

WORKDIR /workspace

CMD ["/usr/local/bin/git-sync"]
