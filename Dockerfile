# Use official Python image
FROM python:3.13.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STORAGE_ROOT=/temp/storage

# Set work directory
WORKDIR /app

# Install pip and system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Copy and set permissions for the startup script
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Create storage directory (will be mounted in production)
RUN mkdir -p /temp/storage

# Set entrypoint
ENTRYPOINT ["/app/start.sh"]
