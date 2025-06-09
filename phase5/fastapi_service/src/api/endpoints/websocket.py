import asyncio

from fastapi import APIRouter, WebSocket
from redis.asyncio import Redis
from src.common.settings import settings

router = APIRouter()


@router.websocket("/live-metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Use async Redis client directly
    redis = Redis(
        host="redis",
        port=6379,
        password=settings.redis_password,
        decode_responses=True,
    )

    pubsub = redis.pubsub()
    await pubsub.subscribe("metrics_updates")

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe("metrics_updates")
        await pubsub.close()
        await redis.close()
