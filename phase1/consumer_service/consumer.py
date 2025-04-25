import json
from datetime import datetime

from confluent_kafka import Consumer

config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "mygroup",
    "auto.offset.reset": "latest",
}
consumer = Consumer(config)

topics = ["app_events"]
consumer.subscribe(topics)
print("Listening to {}".format(", ".join([topic for topic in topics])))

try:
    while True:
        event = consumer.poll(timeout=1.0)

        if event is None:
            continue
        if event.error():
            print("Consumer error {}".format(event.error()))
            continue

        topic = event.topic().encode("utf8")
        key = event.key().decode("utf8") if event.key() else "None"

        data = json.loads(event.value().decode("utf8"))
        print("Event consumed: ")
        print(
            f"➔ Received Event:\n- Key: {event.key().decode('utf-8')}\n- Value: {event.value().decode('utf-8')}"
        )

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
