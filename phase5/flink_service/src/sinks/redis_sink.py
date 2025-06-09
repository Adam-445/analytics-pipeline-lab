import json
import redis
from src.common.settings import settings

# lazy-init a Redis client per Python worker
_redis_client = None

def write_to_redis_with_ttl(record):
    """
    Push each aggregated Row into a Redis sorted set (ZADD) under
    key "metric:<event_type>:<window_size>", score=window_end,
    and reset TTL on the key. Also publish to Pub/Sub channel.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host="redis",
            port=6379,
            password=settings.redis_password,
            db=0,
        )

    client = _redis_client
    key = f"metric:{record.event_type}:{record.window_size}"

    # Create metric data
    metric_data = {
        "window_start":  record.window_start,
        "window_end": record.window_end,
        "count":         record.count,
        "total_value":   record.total_value,
        "unique_users":  record.unique_users,
        "event_type": record.event_type,
        "window_size": record.window_size
    }
    metric_json = json.dumps(metric_data)

    # Pipeline ZADD + EXPIRE + PUBLISH
    pipe = client.pipeline()
    pipe.zadd(key, {metric_json: record.window_end})
    pipe.expire(key, 3600)  # ttl_seconds = 3600
    pipe.publish("metrics_updates", metric_json)
    pipe.execute()

    # map requires a return; VOID is declared so this gets discarded
    return None