# Base image
FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Workdir
WORKDIR /app

# System deps (optional; slim works with psycopg[binary])
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app

# Default command is overridden per service in docker-compose.yml
CMD ["bash", "-lc", "python -V"]
