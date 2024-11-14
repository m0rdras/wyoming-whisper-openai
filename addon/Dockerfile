ARG BUILD_FROM
FROM ${BUILD_FROM}

# Copy local files
COPY rootfs /

# Set up Python environment
WORKDIR /usr/src/app

# Copy Python package files
COPY ../wyoming_whisper_openai_client ./wyoming_whisper_openai_client
COPY ../pyproject.toml ../poetry.lock ../README.md ./

# Install dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
    && pip3 install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && apk del py3-pip

# Make scripts executable
RUN chmod a+x /etc/services.d/whisper/*

# Labels
LABEL \
    io.hass.name="OpenAI Whisper STT" \
    io.hass.description="OpenAI Whisper Speech-to-Text service" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION}

# Entrypoint is handled by S6 overlay
