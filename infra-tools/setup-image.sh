#!/usr/bin/env bash

set -euo pipefail

ARCH="$(dpkg --print-architecture)"

apt-get update
apt-get install -y --no-install-recommends \
  curl \
  gnupg \
  software-properties-common \
  wireguard
add-apt-repository --yes --update ppa:ansible/ansible
apt-get install -y --no-install-recommends ansible
rm -rf /var/lib/apt/lists/*

# Install kubectl
curl -fsSL "https://dl.k8s.io/release/$(curl -fsSL https://dl.k8s.io/release/stable.txt)/bin/linux/${ARCH}/kubectl" -o /tmp/kubectl
install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl
rm -f /tmp/kubectl

# Install Helm
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 -o /tmp/get_helm.sh
chmod 700 /tmp/get_helm.sh
/tmp/get_helm.sh
rm -f /tmp/get_helm.sh

# Install Helmfile
HELMFILE_VERSION="$(curl -fsSL https://api.github.com/repos/helmfile/helmfile/releases/latest | grep tag_name | cut -d '"' -f 4)"
curl -fsSL "https://github.com/helmfile/helmfile/releases/download/${HELMFILE_VERSION}/helmfile_${HELMFILE_VERSION#v}_linux_${ARCH}.tar.gz" -o /tmp/helmfile.tar.gz
tar -xzf /tmp/helmfile.tar.gz -C /tmp
install -o root -g root -m 0755 /tmp/helmfile /usr/local/bin/helmfile
rm -f /tmp/helmfile.tar.gz /tmp/helmfile

# Install OpenTofu
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o /tmp/install-opentofu.sh
chmod +x /tmp/install-opentofu.sh
/tmp/install-opentofu.sh --install-method deb
rm -f /tmp/install-opentofu.sh

# Install Hetzner Cloud CLI
curl -fsSL "https://github.com/hetznercloud/cli/releases/latest/download/hcloud-linux-${ARCH}.tar.gz" -o /tmp/hcloud.tar.gz
tar -C /usr/local/bin --no-same-owner -xzf /tmp/hcloud.tar.gz hcloud
rm -f /tmp/hcloud.tar.gz

# Verify installations
ansible --version
kubectl version --client
helm version
helmfile version
tofu version
hcloud version
