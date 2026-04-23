# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем ВСЮ папку requirements
COPY requirements/ ./requirements/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements/backend.txt

# Runtime stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:$PATH"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Copy alembic files
COPY alembic.ini .
COPY alembic/ ./alembic/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running Alembic migrations..."\n\
alembic upgrade head\n\
echo "Starting FastAPI application..."\n\
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
