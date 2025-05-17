from fastapi import FastAPI
from src.api.endpoints import metrics

app = FastAPI(
    title="Real-Time Metrics API",
    description="Fetch aggregated event metrics from Redis",
    version="1.0.0",
)

# Include routers
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
