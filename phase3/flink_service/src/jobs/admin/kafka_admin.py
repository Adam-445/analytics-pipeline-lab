from confluent_kafka.admin import AdminClient, NewTopic

config = {"bootstrap.servers": "kafka1:19092"}
admin = AdminClient(config)

new_topics = [
    NewTopic(topic, num_partitions=4, replication_factor=1)
    for topic in ["flink-events"]
]

futures = admin.create_topics(new_topics)

# Wait for each operation to finish
for topic ,future in futures.items():
    try:
        future.result()
        print("Topic {} created".format(topic))
    except Exception as e:
        print("Failed to create topic {}: {}".format(topic, e))