# Bootstrap image
# Used for initializing and setting up environments

FROM alpine:3.19

LABEL org.opencontainers.image.source=https://github.com/triimd/images
LABEL org.opencontainers.image.description="Bootstrap image for environment initialization"
LABEL org.opencontainers.image.licenses=MIT

# Install common bootstrap tools
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    git \
    openssh-client \
    ca-certificates \
    jq \
    yq \
    envsubst \
    gettext

# Create bootstrap script
COPY <<'EOF' /usr/local/bin/bootstrap
#!/bin/bash
set -e

echo "Bootstrap starting..."

# Source any bootstrap configuration if provided
if [ -f "/config/bootstrap.sh" ]; then
    echo "Running custom bootstrap configuration..."
    source /config/bootstrap.sh
fi

# Run any command passed as arguments
if [ $# -gt 0 ]; then
    echo "Executing: $@"
    exec "$@"
else
    echo "Bootstrap complete. No additional commands to execute."
fi
EOF

RUN chmod +x /usr/local/bin/bootstrap

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/bootstrap"]
CMD ["/bin/bash"]
