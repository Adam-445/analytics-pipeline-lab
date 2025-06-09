from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import metrics, websocket

def create_app() -> FastAPI:
    app = FastAPI(
        title="Real-Time Metrics API",
        description="Fetch aggregated event metrics from Redis",
        version="1.0.0",
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    # Register routes
    register_routers(app)

    return app

def register_routers(app: FastAPI) -> None:
    routers = [
        (metrics.router, "/metrics", ["metrics"]),
        (websocket.router, "", ["websocket"]),
    ]

    for router, prefix, tags in routers:
        app.include_router(router, prefix=prefix, tags=tags)

app = create_app()
