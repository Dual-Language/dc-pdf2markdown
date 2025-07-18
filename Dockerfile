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

# Install Python dependencies from requirements.txt
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Initialize/download models during build
# RUN python initialize_models.py

# Create storage directory (will be mounted in production)
RUN mkdir -p /temp/storage

# Set entrypoint
ENTRYPOINT ["python3", "main.py"]
