FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    nano \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Poetry 2.1
RUN pip install --no-cache-dir poetry==2.1.0

# Configure Poetry
RUN poetry config virtualenvs.create false


# Create a non-root user
RUN useradd -m -s /bin/bash developer && \
    chown -R developer:developer /workspace
USER developer

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["bash"] 