FROM alpine:3.21

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Bootstrap image for environment initialization"
LABEL org.opencontainers.image.licenses=MIT

COPY setup-image.sh /tmp/setup-image.sh
RUN sh /tmp/setup-image.sh && rm -f /tmp/setup-image.sh

COPY bootstrap.sh /usr/local/bin/bootstrap
RUN chmod +x /usr/local/bin/bootstrap

USER bootstrap

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/bootstrap"]
CMD ["/bin/bash"]
