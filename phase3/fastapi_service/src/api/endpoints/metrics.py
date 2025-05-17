from fastapi import APIRouter, HTTPException, Query
from typing import List
import json

from src.clients.redis_client import RedisClient
from src.schemas.metrics import MetricsResponse, MetricEntry

router = APIRouter()

@router.get("/", response_model=MetricsResponse)
def get_metrics(
    event_type: str = Query(..., description="Event type to query"),
    window_size: str = Query(..., description="Window size, e.g., '30s'"),
    limit: int = Query(10, gt=0, le=100, description="Max number of entries to return"),
):
    client = RedisClient.get_client()
    key = f"metric:{event_type}:{window_size}"
    # ZREVRANGE sorted by score descending
    raw = client.zrevrange(key, 0, limit - 1, withscores=False)

    if not raw:
        raise HTTPException(status_code=404, detail="No metrics found")

    entries = []
    for item in raw:
        data = json.loads(item)
        entries.append(MetricEntry(**data))

    return MetricsResponse(
        event_type=event_type,
        window_size=window_size,
        entries=entries,
    )