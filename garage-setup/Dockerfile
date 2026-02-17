FROM alpine:3.23

ARG GARAGE_VERSION=v2.2.0
ARG KUBECTL_VERSION=v1.35.0

RUN apk add --no-cache \
    bash \
    ca-certificates \
    curl \
    jq \
    python3 \
    tar

RUN curl -fsSL "https://releases.garage.deuxfleurs.fr/${GARAGE_VERSION}/garage-${GARAGE_VERSION}-linux-amd64" \
    -o /usr/local/bin/garage && \
  chmod +x /usr/local/bin/garage

RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o /usr/local/bin/kubectl && \
  chmod +x /usr/local/bin/kubectl

WORKDIR /usr/local/bin
