import json

from pyflink.common import Row
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.time import Duration, Time
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import TimestampAssigner, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.datastream.window import SlidingEventTimeWindows

from src.sinks.redis_sink import write_to_redis_with_ttl


class EventTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value: Row, record_timestamp: int) -> int:
        # event.timestamp is in seconds; convert to millis
        return int(value.timestamp * 1000) # type: ignore


class WindowAggregator(ProcessWindowFunction):
    def __init__(self, window_size):
        self.window_size = window_size

    def process(self, key: str, context: ProcessWindowFunction.Context, elements):
        # materialize so we can count + sum
        elems = list(elements)
        count = len(elems)
        total_value = sum(e.value for e in elems)
        unique_users = len(set(e.user_id for e in elems))
        yield Row(
            event_type=key,
            window_size=self.window_size,
            window_start=context.window().start,
            window_end=context.window().end,
            count=count,
            total_value=total_value,
            unique_users=unique_users,
        )


def parse_and_validate(event_str: str):
    try:
        data = json.loads(event_str)
        if not all(k in data for k in ("user_id", "timestamp", "value", "event_type")):
            return []
        return [
            Row(
                user_id=str(data["user_id"]),
                event_type=str(data["event_type"]),
                timestamp=float(data["timestamp"]),
                value=float(data["value"]),
            )
        ]
    except (json.JSONDecodeError, ValueError, TypeError):
        return []


def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    # Kafka source
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers("kafka1:19092")
        .set_topics("flink-events")
        .set_group_id("flink-consumer-group")
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # Watermark strategy
    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(EventTimestampAssigner())
        .with_idleness(Duration.of_seconds(5))
    )

    stream = env.from_source(kafka_source, watermark_strategy, "KafkaSource")

    parsed = stream.flat_map(
        parse_and_validate,
        output_type=Types.ROW_NAMED(
            ["user_id", "event_type", "timestamp", "value"],
            [Types.STRING(), Types.STRING(), Types.DOUBLE(), Types.DOUBLE()],
        ),
    )

    # Key, window, and process
    window_size = "30s"
    aggregated = (
        parsed.key_by(lambda e: e.event_type, key_type=Types.STRING())
        .window(SlidingEventTimeWindows.of(Time.seconds(30), Time.seconds(10)))
        .process(
            WindowAggregator(window_size=window_size),
            output_type=Types.ROW_NAMED(
                [
                    "event_type",
                    "window_size",
                    "window_start",
                    "window_end",
                    "count",
                    "total_value",
                    "unique_users",
                ],
                [
                    Types.STRING(),
                    Types.STRING(),
                    Types.LONG(),
                    Types.LONG(),
                    Types.LONG(),
                    Types.DOUBLE(),
                    Types.LONG(),
                ],
            ),
        )
    )
    aggregated.map(write_to_redis_with_ttl)
    # Format and print
    aggregated.map(
        lambda x: (
            f"Window [{x.window_start} – {x.window_end}] "
            f"event_type={x.event_type} | count={x.count} | total_value={x.total_value:.2f}"
        ),
        output_type=Types.STRING(),
    ).print()

    env.execute("Kafka Event Aggregation")


if __name__ == "__main__":
    main()
