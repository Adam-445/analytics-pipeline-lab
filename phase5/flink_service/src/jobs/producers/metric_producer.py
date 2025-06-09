import json
import random
import time

from confluent_kafka import Producer

KAFKA_BROKER = "kafka1:19092"
TOPIC = "flink-events"

# Test data setup
USER_IDS = [f"user_{i}" for i in range(1, 6)]  # 5 test users
EVENT_TYPES = ["click", "purchase", "view", "login", "logout"]
MIN_VALUE = 1
MAX_VALUE = 100
EVENT_INTERVAL = 0.5  # seconds between events


def delivery_report(err, msg):
    if err:
        print(f"Message failed delivery: {err}")
    else:
        event_data = json.loads(msg.value())
        print(
            f"Produced {event_data['event_type']} event for {event_data['user_id']} "
            f"with value {event_data['value']}"
        )


producer = Producer({"bootstrap.servers": KAFKA_BROKER})


def generate_event():
    return {
        "user_id": random.choice(USER_IDS),
        "event_type": random.choice(EVENT_TYPES),
        "value": round(random.uniform(MIN_VALUE, MAX_VALUE), 2),
        "timestamp": time.time(),
    }


try:
    while True:
        event_data = generate_event()

        # Produce with user_id as both message key and in payload
        producer.produce(
            topic=TOPIC,
            key=event_data["user_id"],
            value=json.dumps(event_data),
            callback=delivery_report,
        )

        # Trigger any available delivery report callbacks
        producer.poll(0)

        # Randomize sleep time slightly for more realistic distribution
        time.sleep(random.uniform(EVENT_INTERVAL * 0.5, EVENT_INTERVAL * 1.5))

except KeyboardInterrupt:
    print("\nFlushing remaining messages...")
    producer.flush()
