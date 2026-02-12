FROM node:20-bookworm

ARG IMAGE_SOURCE_URL=https://code.example.com/triimd/images

LABEL org.opencontainers.image.source=${IMAGE_SOURCE_URL}
LABEL org.opencontainers.image.description="Lightweight job runtime image"
LABEL org.opencontainers.image.licenses=MIT

COPY setup-image.sh /tmp/setup-image.sh
RUN bash /tmp/setup-image.sh && rm -f /tmp/setup-image.sh

WORKDIR /workspace

USER node

CMD ["bash"]
