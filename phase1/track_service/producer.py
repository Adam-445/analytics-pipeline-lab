import json
import random
import uuid
from datetime import datetime

from confluent_kafka import Producer

config = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
    "batch.size": 1_048_576,  # 1MB batches
    "linger.ms": 20,  # Wait up to 20ms for batching
    "enable.idempotence": True,  # Ensure exactly-once semantics
}


def delivery_report(err, msg):
    """Simplified error-only reporting"""
    if err is not None:
        print(f"Message delivery failed: {err}")


def produce_event(event: dict):
    """Main production logic"""
    producer = Producer(config)

    try:
        producer.produce(
            topic="app_events",
            value=json.dumps(event),
            key=str(uuid.uuid4()),
            callback=delivery_report,
        )

        # Final poll and flush
        producer.poll(0)
        producer.flush()

    except Exception as e:
        print(f"Production failed: {e}")