# Use official Python image
FROM python:3.13.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STORAGE_ROOT=/temp/storage

# Set work directory
WORKDIR /app

# Install pip and system dependencies (including WeasyPrint dependencies)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        dos2unix \
        curl \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libfontconfig1 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

RUN dos2unix /app/start.sh

# Ensure start.sh has proper permissions and LF line endings
RUN dos2unix /app/start.sh && chmod +x /app/start.sh

# Create storage directory (will be mounted in production)
RUN mkdir -p /temp/storage

EXPOSE 3000

# Set entrypoint
ENTRYPOINT ["/app/start.sh"]
