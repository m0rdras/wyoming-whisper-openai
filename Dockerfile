# Build stage
FROM python:3.13-slim as builder

# Install poetry
RUN pip install poetry

# Copy only the files needed for installation
WORKDIR /app
COPY pyproject.toml poetry.lock README.md ./
COPY wyoming_whisper_openai_client ./wyoming_whisper_openai_client

# Build wheel file
RUN poetry build --format wheel

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

# Copy wheel from builder and install it
COPY --from=builder /app/dist/*.whl ./
RUN pip install --no-cache-dir *.whl \
    && rm *.whl

# Copy run script
COPY run.sh ./
RUN chmod +x run.sh

# Set environment variables
ENV OPENAI_API_KEY=""
ENV WHISPER_LANGUAGE=""

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 7891

ENTRYPOINT ["./run.sh"]
