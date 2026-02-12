#!/usr/bin/env bash

set -euo pipefail

USERNAME="${USERNAME:-dev}"
USER_UID="${USER_UID:-1000}"
USER_GID="${USER_GID:-1000}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"

apt-get update
apt-get install -y --no-install-recommends \
  neovim \
  pipx \
  tmux \
  zsh
rm -rf /var/lib/apt/lists/*

if getent group "${USER_GID}" >/dev/null; then
  existing_group="$(getent group "${USER_GID}" | cut -d: -f1)"
  if [ "${existing_group}" != "${USERNAME}" ]; then
    groupmod -n "${USERNAME}" "${existing_group}"
  fi
elif getent group "${USERNAME}" >/dev/null; then
  groupmod --gid "${USER_GID}" "${USERNAME}"
else
  groupadd --gid "${USER_GID}" "${USERNAME}"
fi

if id -u "${USER_UID}" >/dev/null 2>&1; then
  existing_user="$(getent passwd "${USER_UID}" | cut -d: -f1)"
  if [ "${existing_user}" != "${USERNAME}" ]; then
    usermod -l "${USERNAME}" "${existing_user}"
  fi
  usermod --home "/home/${USERNAME}" --move-home --shell /bin/zsh --gid "${USER_GID}" "${USERNAME}"
elif id -u "${USERNAME}" >/dev/null 2>&1; then
  usermod --uid "${USER_UID}" --gid "${USER_GID}" --home "/home/${USERNAME}" --move-home --shell /bin/zsh "${USERNAME}"
else
  useradd --uid "${USER_UID}" --gid "${USER_GID}" -m -s /bin/zsh "${USERNAME}"
fi

printf "Defaults !admin_flag\n" > /etc/sudoers.d/00-disable-admin-flag
printf "%s ALL=(ALL) NOPASSWD: ALL\n" "${USERNAME}" > "/etc/sudoers.d/90-${USERNAME}"
chmod 0440 /etc/sudoers.d/00-disable-admin-flag "/etc/sudoers.d/90-${USERNAME}"

install -d -m 0755 "${WORKSPACE_DIR}"
chown "${USER_UID}:${USER_GID}" "${WORKSPACE_DIR}"
rm -f "/home/${USERNAME}/.bashrc" "/home/${USERNAME}/.bash_logout" "/home/${USERNAME}/.profile"

install -d -o "${USER_UID}" -g "${USER_GID}" \
  "/home/${USERNAME}/.cache" \
  "/home/${USERNAME}/.config" \
  "/home/${USERNAME}/.config/npm" \
  "/home/${USERNAME}/.config/tmux" \
  "/home/${USERNAME}/.config/zsh" \
  "/home/${USERNAME}/.docker" \
  "/home/${USERNAME}/.local/bin" \
  "/home/${USERNAME}/.local/pipx" \
  "/home/${USERNAME}/.local/share" \
  "/home/${USERNAME}/.local/state"

install -o "${USER_UID}" -g "${USER_GID}" -m 0644 /tmp/zshenv "/home/${USERNAME}/.config/zsh/.zshenv"
install -o "${USER_UID}" -g "${USER_GID}" -m 0644 /tmp/zshrc "/home/${USERNAME}/.config/zsh/.zshrc"
install -o "${USER_UID}" -g "${USER_GID}" -m 0644 /tmp/tmux.conf "/home/${USERNAME}/.config/tmux/tmux.conf"
