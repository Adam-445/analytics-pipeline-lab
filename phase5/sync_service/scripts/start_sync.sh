#!/bin/bash
set -e

echo "[INFO] Waiting for Postgres..."
while ! pg_isready -h postgres -U admin -d analytics; do
    echo "Waiting for Postgres to start..."
    sleep 2
done

echo "[INFO] Waiting for Redis..."
while ! redis-cli -h redis -a ${REDIS_PASSWORD} ping > /dev/null 2>&1; do
    echo "Waiting for Redis to start..."
    sleep 2
done

echo "[INFO] All dependencies are ready. Starting sync job..."
exec python -u /app/src/sync_job.py