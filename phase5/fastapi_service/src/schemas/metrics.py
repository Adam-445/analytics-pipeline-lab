from pydantic import BaseModel
from typing import Optional, List

class MetricEntry(BaseModel):
    window_start: int
    count: int
    total_value: float
    unique_users: int

class MetricsResponse(BaseModel):
    event_type: str
    window_size: str
    entries: List[MetricEntry]