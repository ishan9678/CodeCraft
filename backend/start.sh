#!/bin/bash

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run Alembic migrations
echo "Running database migrations..."
alembic -c /app/src/alembic.ini upgrade head

# Move into the `src` directory
cd /app/src

# Start the backend app
echo "Starting FastAPI server..."
exec gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 llama_agent:app