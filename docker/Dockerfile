# =============================================================================
# Multi-stage Dockerfile for AI Transactional Agent API
# =============================================================================
# Stage 1: Base with Python 3.12
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# =============================================================================
# Stage 2: Dependencies
FROM base AS dependencies

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY .python-version ./

# Install dependencies
RUN uv sync --frozen --no-dev

# =============================================================================
# Stage 3: Production
FROM base AS production

WORKDIR /app

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY apps/ /app/apps/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn apps.main:app --host 0.0.0.0 --port 8000"]