FROM dxflrs/garage:v2.2.0 AS garage
FROM alpine:3.23

ARG KUBECTL_VERSION=v1.35.0
ARG TARGETARCH

# Install minimal runtime deps
RUN apk add --no-cache \
    ca-certificates \
    curl \
    bash \
 && update-ca-certificates

# Install kubectl (multi-arch aware)
RUN curl -fsSLO \
      "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" \
 && curl -fsSLO \
      "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl.sha256" \
 && echo "$(cat kubectl.sha256)  kubectl" | sha256sum -c - \
 && install -m 0755 kubectl /usr/local/bin/kubectl \
 && rm kubectl kubectl.sha256

# Copy garage binary from official image
COPY --from=garage /garage /usr/local/bin/garage

# Create non-root user
RUN adduser -D -H -s /sbin/nologin appuser \
 && chown appuser:appuser /usr/local/bin/garage /usr/local/bin/kubectl

USER appuser

WORKDIR /workspace

ENTRYPOINT ["/bin/bash"]

