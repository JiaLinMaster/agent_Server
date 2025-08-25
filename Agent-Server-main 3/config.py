import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD')
    API_KEY: str = os.getenv('OPENAI_API_KEY')
    BASE_URL: str = os.getenv('BASE_URL')
    MODEL_NAME: str = os.getenv('MODEL_NAME') or "deepseek-v3"
    LOGGING_LEVEL: str = os.getenv('LOGGING_LEVEL') or "INFO"
    MODEL_TEMPERATURE: float = os.getenv('MODEL_TEMPERATURE') or 0.2
    # KAFKA_BOOTSTRAP_SERVERS: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    # KAFKA_TOPIC: str = os.getenv('KAFKA_TOPIC')

    class Config:
        env_file = ".env"

settings = Settings()