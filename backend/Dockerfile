# ==============================================================================
# Multi-stage Dockerfile for Production GCP Deployment
# Optimized for faster builds and smaller final image
# ==============================================================================

# Stage 1: Base Python with system dependencies
FROM python:3.11-slim as base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Stage 2: Build environment with all build dependencies
FROM python:3.11-slim as builder
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip to latest stable version
RUN pip install --no-cache-dir --upgrade pip==25.2

# Copy requirements
COPY requirements.txt /tmp/requirements.txt

# Install all requirements from file to avoid conflicts and ensure consistency
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 3: Production runtime
FROM base as production

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash validatus && \
    chown -R validatus:validatus /app
USER validatus

# Copy application code
COPY --chown=validatus:validatus . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Use gunicorn with uvicorn worker for better production performance
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]
