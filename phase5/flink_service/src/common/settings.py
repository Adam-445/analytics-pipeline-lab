from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_password: str = "redispass"

settings = Settings()