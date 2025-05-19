import json
import redis
from src.common.settings import settings

# lazy-init a Redis client per Python worker
_redis_client = None

def write_to_redis_with_ttl(record):
    """
    Push each aggregated Row into a Redis sorted set (ZADD) under
    key "metric:<event_type>:<window_size>", score=window_end,
    and reset TTL on the key.
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
    # metric_data as JSON string (we use it as the member in ZSET)
    metric_data = json.dumps({
        "window_start":  record.window_start,
        "count":         record.count,
        "total_value":   record.total_value,
        "unique_users":  record.unique_users,
    })

    # Pipeline ZADD + EXPIRE
    pipe = client.pipeline()
    pipe.zadd(key, {metric_data: record.window_end})
    pipe.expire(key, 3600)  # ttl_seconds = 3600
    pipe.execute()

    # map requires a return; VOID is declared so this gets discarded
    return None