ARG BASE_IMAGE=infra-tools:latest
FROM ${BASE_IMAGE}

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000
ARG WORKSPACE_DIR=/workspace

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Python development image built on infra-tools"
LABEL org.opencontainers.image.licenses=MIT

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY setup-dev-user.sh /tmp/setup-dev-user.sh
COPY zshenv /tmp/zshenv
COPY zshrc /tmp/zshrc
COPY tmux.conf /tmp/tmux.conf

RUN USERNAME="${USERNAME}" USER_UID="${USER_UID}" USER_GID="${USER_GID}" WORKSPACE_DIR="${WORKSPACE_DIR}" bash /tmp/setup-dev-user.sh && \
    rm -f /tmp/setup-dev-user.sh /tmp/zshenv /tmp/zshrc /tmp/tmux.conf

ENV DF_DEV=true \
    USER=${USERNAME} \
    HOME=/home/${USERNAME} \
    XDG_CACHE_HOME=/home/${USERNAME}/.cache \
    XDG_CONFIG_HOME=/home/${USERNAME}/.config \
    XDG_DATA_HOME=/home/${USERNAME}/.local/share \
    XDG_STATE_HOME=/home/${USERNAME}/.local/state \
    ZDOTDIR=/home/${USERNAME}/.config/zsh \
    DOCKER_CONFIG=/home/${USERNAME}/.docker \
    PIPX_HOME=/home/${USERNAME}/.local/pipx \
    PIPX_BIN_DIR=/home/${USERNAME}/.local/bin \
    PATH=/home/${USERNAME}/.local/bin:${PATH}

COPY install-packages.sh /tmp/install-packages.sh

RUN install -o "${USER_UID}" -g "${USER_GID}" -m 0755 /tmp/install-packages.sh "/home/${USERNAME}/.cache/install-packages.sh" && \
    rm -f /tmp/install-packages.sh

USER ${USERNAME}

RUN bash "/home/${USERNAME}/.cache/install-packages.sh" && \
    rm -f "/home/${USERNAME}/.cache/install-packages.sh"

WORKDIR ${WORKSPACE_DIR}

CMD ["zsh"]
