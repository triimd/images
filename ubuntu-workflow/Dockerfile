# Ubuntu-based image for GitHub Actions workflows, act, and gitea
# Includes common tools needed for CI/CD workflows

FROM ubuntu:22.04

LABEL org.opencontainers.image.source=https://github.com/triimd/images
LABEL org.opencontainers.image.description="Ubuntu-based image for GitHub Actions workflows, act, and gitea"
LABEL org.opencontainers.image.licenses=MIT

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install common workflow tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    jq \
    build-essential \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip \
    zip \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for Docker-in-Docker scenarios)
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

CMD ["/bin/bash"]
