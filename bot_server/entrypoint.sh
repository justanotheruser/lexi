#!/bin/bash
set -e

# Get database credentials from environment variables
DB_USER="${POSTGRES__USER:-$POSTGRES_USER}"
DB_NAME="${POSTGRES__DB:-$POSTGRES_DB}"
DB_HOST="${POSTGRES__HOST:-db}"
DB_PORT="${POSTGRES__PORT:-5432}"

echo "Waiting for database to be ready..."
echo "Using database: $DB_NAME, user: $DB_USER, host: $DB_HOST, port: $DB_PORT"

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Migrations completed. Starting application..."
exec python -m lexi.main 