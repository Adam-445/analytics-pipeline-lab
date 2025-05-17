#!/bin/bash
set -e

# Wait for Kafka to be ready
echo "[INFO] Waiting for Kafka..."
while ! nc -z kafka1 19092; do
  sleep 1
done

# Create Kafka Topic
echo "[INFO] Creating Kafka topic..."
python -m src.jobs.admin.kafka_admin

# Submit Flink Job
flink run \
  --jobmanager jobmanager:8081 \
  --python src/jobs/consumers/metric_consumer.py\