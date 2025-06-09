import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.clients.db import get_db
from src.clients.redis_client import RedisClient
from src.models.app_event import AppEvent
from src.schemas.metrics import MetricEntry, MetricsResponse

router = APIRouter()


@router.get("/realtime", response_model=MetricsResponse)
def get_metrics_realtime(
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


@router.get("/history", response_model=MetricsResponse)
def get_metrics_history(
    event_type: str = Query(..., description="Event type to query"),
    window_size: str = Query(..., description="Window size, e.g., '30s'"),
    start_time: Optional[datetime] = Query(
        None, description="Start time in ISO format"
    ),
    end_time: Optional[datetime] = Query(None, description="End time in ISO format"),
    limit: int = Query(10, gt=0, le=100, description="Max number of entries to return"),
    db: Session = Depends(get_db),
):
    query = db.query(AppEvent).filter(
        AppEvent.event_type == event_type,
        AppEvent.window_size == window_size,
    )
    if start_time:
        query = query.filter(AppEvent.window_start >= start_time)
    if end_time:
        query = query.filter(AppEvent.window_start <= end_time)
    results = query.order_by(AppEvent.window_start.desc()).limit(limit).all()
    metrics = [
        MetricEntry(
            window_start=int(app_event.window_start.timestamp() * 1000),
            count=app_event.count,
            total_value=app_event.total_value,
            unique_users=app_event.unique_users,
        )
        for app_event in results
    ]
    if not results:
        raise HTTPException(status_code=404, detail="No metrics found")
    return MetricsResponse(
        event_type=event_type,
        window_size=window_size,
        entries=metrics,
    )