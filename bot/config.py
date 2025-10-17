# bot/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

def find_env_file():
    """Find .env file in current or parent directories"""
    current = Path.cwd()
    
    # Check current directory
    if (current / '.env').exists():
        return str(current / '.env')
    
    # Check parent directories (up to 3 levels)
    for _ in range(3):
        current = current.parent
        if (current / '.env').exists():
            return str(current / '.env')
    
    # Default to .env in current directory
    return '.env'

class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str
    
    # Database
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    # Redis
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: str = ""
    redis_chat_history_limit: int = 5
    
    # RabbitMQ
    rabbitmq_host: str
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    rabbitmq_queue: str = "astrology_requests"
    rabbitmq_workers: int = 1
    
    # Ollama
    ollama_host: str
    ollama_model: str
    enable_thinking: bool = True
    thinking_max_tokens: int = 2000
    thinking_temperature: float = 0.7
    
    # Services
    mem0_service_url: str
    astrology_api_url: str
    
    # User Management
    max_strikes: int = 3
    enable_profanity_filter: bool = True
    
    # Chat Encryption
    chat_encryption_key: str
    
    # App
    log_level: str = "INFO"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
    
    class Config:
        env_file = find_env_file()
        env_file_encoding = 'utf-8'
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()