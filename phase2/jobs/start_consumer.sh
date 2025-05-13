#!/bin/bash
set -e

# --------------------------
# 1. Wait for Kafka to be ready
# --------------------------
echo "[INFO] Waiting for Kafka..."
while ! nc -z kafka1 19092; do
  sleep 1
done

# --------------------------
# 2. Create Kafka Topic
# --------------------------
echo "[INFO] Creating Kafka topic..."
python admin.py

# --------------------------
# 3. Submit Flink Job
# --------------------------
flink run --jobmanager jobmanager:8081 --parallelism 1 --python /jobs/flink_consumer.py