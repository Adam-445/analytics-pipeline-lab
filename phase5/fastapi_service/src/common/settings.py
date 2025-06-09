from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_password: str = "redispass"
    postgres_password: str = "postgrespass"

settings = Settings()