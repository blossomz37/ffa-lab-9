# Multi-stage Dockerfile for FFA Lab 9 - MCP Writing Tools
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Development stage
FROM base as development
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Copy source code
COPY tools/ ./tools/
COPY tests/ ./tests/
COPY samples/ ./samples/

# Production stage
FROM base as production

# Copy only necessary files
COPY tools/ ./tools/
COPY samples/ ./samples/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "-m", "tools.writers_room_v2", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import tools.memory_mcp; print('OK')" || exit 1
