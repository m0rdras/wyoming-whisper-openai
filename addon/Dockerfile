ARG BUILD_FROM
FROM $BUILD_FROM

# Add S6 overlay
WORKDIR /usr/src

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        git

# Copy local files
COPY rootfs /

# Install the package
WORKDIR /usr/src
COPY . .
RUN pip3 install --no-cache-dir .

# Labels
LABEL \
    io.hass.name="OpenAI Whisper STT" \
    io.hass.description="OpenAI Whisper Speech-to-Text service" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    io.hass.arch=${BUILD_ARCH}
