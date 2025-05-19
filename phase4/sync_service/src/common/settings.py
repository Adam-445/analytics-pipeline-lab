from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_password: str = "redispass"
    postgres_password: str = "postgrespass"
    sync_interval_seconds: int = 60

settings = Settings()