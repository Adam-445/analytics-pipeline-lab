import json
import time
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from src.common.database import engine, session_scope
from src.common.models import AppEvent, Base
from src.common.redis_client import RedisClient
from src.common.settings import settings

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")


def fetch_metrics_from_redis(redis_client):
    keys = redis_client.keys("metric:*")
    metrics = []
    redis_entries = []  # Track (key, member) for deletion
    for key in keys:
        event_type, window_size = key.split(":")[1:]
        records = redis_client.zrange(key, 0, -1)
        for record in records:
            metric = json.loads(record)
            metrics.append(
                {
                    "window_start": datetime.fromtimestamp(
                        metric["window_start"] / 1000
                    ),
                    "event_type": event_type,
                    "count": metric["count"],
                    "total_value": metric["total_value"],
                    "unique_users": metric["unique_users"],
                    "window_size": window_size,
                }
            )
            redis_entries.append((key, record))  # Save for later deletion
    return metrics, redis_entries


def delete_metrics_from_redis(redis_client, redis_entries):
    for key, member in redis_entries:
        redis_client.zrem(key, member)


def main():
    print("[INFO] Starting sync job...")
    while True:
        try:
            redis_client = RedisClient.get_client()

            print("[INFO] Fetching metrics from Redis...")
            metric_dicts, redis_entries = fetch_metrics_from_redis(redis_client)

            if metric_dicts:
                print(
                    f"[INFO] Converting {len(metric_dicts)} metrics to AppEvent objects..."
                )
                metrics = [AppEvent(**metric_dict) for metric_dict in metric_dicts]

                print(f"[INFO] Inserting {len(metrics)} metrics into Postgres...")
                with session_scope() as db:
                    db.add_all(metrics)

                print("[INFO] Metrics inserted successfully. Deleting from Redis...")
                delete_metrics_from_redis(redis_client, redis_entries)
                print("[INFO] Metrics deleted from Redis.")
            else:
                print("[INFO] No metrics to insert.")

        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")

        time.sleep(settings.sync_interval_seconds)


main()
