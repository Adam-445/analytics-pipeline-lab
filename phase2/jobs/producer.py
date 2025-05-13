from confluent_kafka import Producer
import time
import json
import random

KAFKA_BROKER = "kafka1:19092"
TOPIC = "flink-events"

EVENT_IDS = [42, 55, 17]

def delivery_report(err, msg):
    if err:
        print(f"Message failed delivery: {err}")
    else:
        print(f"Mesage delivered to {msg.topic()} [{msg.partition()}]")

producer = Producer({"bootstrap.servers": KAFKA_BROKER})

while True:
    data = {
        "event_id": random.choice(EVENT_IDS),
        "value": random.randint(1, 100),
        "timestamp": time.time()
    }
    producer.produce(TOPIC, json.dumps(data), callback=delivery_report)
    producer.poll(1)
    time.sleep(1)