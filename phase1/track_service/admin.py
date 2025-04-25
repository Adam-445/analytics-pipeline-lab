from confluent_kafka.admin import AdminClient, NewTopic

config = {"bootstrap.servers": "localhost:9092"}
admin = AdminClient(config)

new_topics = [
    NewTopic(topic, num_partitions=4, replication_factor=1) for topic in ["app_events"]
]


if __name__ == "__main__":
    futures = admin.create_topics(new_topics)

    # Wait for each operation to finish
    for topic, future in futures.items():
        try:
            future.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
