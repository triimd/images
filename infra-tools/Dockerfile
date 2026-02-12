FROM ubuntu:24.04

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Ubuntu workflow tooling base image"
LABEL org.opencontainers.image.licenses=MIT

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG DEBIAN_FRONTEND=noninteractive
ARG WORKSPACE_DIR=/workspace

COPY setup-image.sh /tmp/setup-image.sh

RUN bash /tmp/install-packages.sh && \
    rm -f /tmp/install-packages.sh && \
    install -d -m 0755 "${WORKSPACE_DIR}"

WORKDIR ${WORKSPACE_DIR}

CMD ["bash"]
