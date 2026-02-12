FROM catthehacker/ubuntu:act-latest

ENV PATH="/root/.local/bin:${PATH}"

# Install Ansible and system dependencies
RUN apt-get update &&
  apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    software-properties-common \
    wireguard &&
  add-apt-repository --yes --update ppa:ansible/ansible &&
  apt-get install -y ansible &&
  rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" &&
  install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl &&
  rm kubectl

# Install Helm
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 &&
  chmod 700 get_helm.sh &&
  ./get_helm.sh &&
  rm get_helm.sh

# Install Helmfile
RUN HELMFILE_VERSION=$(curl -s https://api.github.com/repos/helmfile/helmfile/releases/latest | grep tag_name | cut -d '"' -f 4) &&
  curl -Lo helmfile.tar.gz "https://github.com/helmfile/helmfile/releases/download/${HELMFILE_VERSION}/helmfile_$(echo ${HELMFILE_VERSION} | sed 's/v//')_linux_amd64.tar.gz" &&
  tar -xzf helmfile.tar.gz &&
  mv helmfile /usr/local/bin/helmfile &&
  chmod +x /usr/local/bin/helmfile &&
  rm helmfile.tar.gz

# Install OpenTofu
RUN curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh &&
  chmod +x install-opentofu.sh &&
  ./install-opentofu.sh --install-method deb &&
  rm install-opentofu.sh

# Install Hetzner Cloud CLI
RUN curl -sSLO https://github.com/hetznercloud/cli/releases/latest/download/hcloud-linux-amd64.tar.gz &&
  tar -C /usr/local/bin --no-same-owner -xzf hcloud-linux-amd64.tar.gz hcloud &&
  rm hcloud-linux-amd64.tar.gz

# Verify installations
RUN ansible --version &&
  kubectl version --client &&
  helm version &&
  helmfile version &&
  tofu version &&
  hcloud version
