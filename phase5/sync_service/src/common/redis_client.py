from redis import Redis
from src.common.settings import settings


class RedisClient:
    _client: Redis | None = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._client is None:
            cls._client = Redis(
                host="redis",
                port=6379,
                password=settings.redis_password,
                decode_responses=True,
            )
        return cls._client
