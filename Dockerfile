# Multi-stage Dockerfile for FFA Lab 9 - MCP Writing Tools
FROM python:3.11-slim-bullseye AS base

# Install security updates
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Development stage
FROM base AS development
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Copy source code
COPY tools/ ./tools/
COPY tests/ ./tests/
COPY samples/ ./samples/

# Production stage
FROM base AS production

# Copy only necessary files
COPY tools/ ./tools/
COPY samples/ ./samples/

# Expose port for API server
EXPOSE 8000

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command - run the emotion arc API server
CMD ["python", "tools/emotion_arc_api_server.py", "--host", "0.0.0.0", "--port", "8000"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
