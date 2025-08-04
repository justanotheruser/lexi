# Build stage - install dependencies with Poetry
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
# Configure Poetry to not create virtual environment and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root


# Runtime stage - clean image with only required packages
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY assets/ ./assets/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port for FastAPI server
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start the application (Telegram bot with FastAPI)
CMD ["python", "-m", "app.main"]
