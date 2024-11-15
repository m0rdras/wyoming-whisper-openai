# Build stage
FROM python:3.13-slim AS builder

# Install poetry
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install poetry

# Copy dependency files first to leverage cache
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install build dependencies and configure poetry
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    python -m venv /venv && \
    poetry config virtualenvs.create false && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes

# Copy source code
COPY wyoming_whisper_openai ./wyoming_whisper_openai
COPY README.md ./

# Build wheel file
RUN poetry build --format wheel

# Runtime stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OPENAI_API_KEY="" \
    WHISPER_LANGUAGE="" \
    PROMPT=""

# Create non-root user first to avoid permission issues
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -s /sbin/nologin -d /app appuser && \
    mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

# Copy wheel and requirements from builder
COPY --from=builder /app/dist/*.whl ./
COPY --from=builder /app/requirements.txt ./

# Install dependencies and cleanup in one layer
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    pip install -r requirements.txt *.whl && \
    rm -rf /var/lib/apt/lists/* *.whl requirements.txt && \
    apt-get clean

# Copy run script
COPY --chown=appuser:appgroup run.sh ./
RUN chmod +x run.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 7891

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["./run.sh"]
