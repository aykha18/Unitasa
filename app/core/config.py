"""
Configuration settings for Unitasa
Handles both development and production environments
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables from .env file
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitasa"))
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "unitasa-secret-key-change-in-production"))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class WiseSettings(BaseSettings):
    """Wise payment configuration"""
    api_key: str = ""
    profile_id: str = ""
    webhook_secret: str = ""
    environment: str = "sandbox"  # sandbox or live
    
    class Config:
        env_prefix = "WISE_"


class OpenAISettings(BaseSettings):
    """OpenAI configuration"""
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096


class OpenRouterSettings(BaseSettings):
    """OpenRouter configuration"""
    api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    model: str = "anthropic/claude-3-haiku"
    temperature: float = 0.7
    max_tokens: int = 4096
    cost_per_1k_tokens: float = 0.00025


class GroqSettings(BaseSettings):
    """Groq configuration"""
    api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model: str = "llama2-70b-4096"
    temperature: float = 0.7
    max_tokens: int = 4096
    cost_per_1k_tokens: float = 0.0007


class EmailSettings(BaseSettings):
    """Email configuration"""
    sendgrid_api_key: str = Field(default_factory=lambda: os.getenv("SENDGRID_API_KEY", ""))
    from_email: str = Field(default_factory=lambda: os.getenv("FROM_EMAIL", "support@unitasa.in"))
    support_email: str = Field(default_factory=lambda: os.getenv("SUPPORT_EMAIL", "support@unitasa.in"))
    from_name: str = "Unitasa"


# class StripeSettings(BaseSettings):
#     """Stripe payment configuration"""
#     api_key: str = Field(default_factory=lambda: os.getenv("STRIPE_API_KEY", ""))
#     webhook_secret: str = Field(default_factory=lambda: os.getenv("STRIPE_WEBHOOK_SECRET", ""))


class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))


class ChromaSettings(BaseSettings):
    """ChromaDB configuration"""
    collection_name: str = "marketing_knowledge"
    persist_directory: str = "./chroma_db"


class EmbeddingsSettings(BaseSettings):
    """Embeddings configuration"""
    model: str = "text-embedding-3-large"
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))


class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = "Unitasa"
    app_description: str = "Unified Marketing Intelligence Platform"
    version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    frontend_url: str = Field(default_factory=lambda: os.getenv("FRONTEND_URL", "http://localhost:3000"))

    # Direct environment variables (for backward compatibility)
    secret_key: Optional[str] = Field(default_factory=lambda: os.getenv("SECRET_KEY"))
    sendgrid_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("SENDGRID_API_KEY"))
    from_email: Optional[str] = Field(default_factory=lambda: os.getenv("FROM_EMAIL"))
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    wise: WiseSettings = Field(default_factory=WiseSettings)
    # stripe: StripeSettings = Field(default_factory=StripeSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    embeddings: EmbeddingsSettings = Field(default_factory=EmbeddingsSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    
    # Railway specific
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    railway_environment: Optional[str] = Field(default_factory=lambda: os.getenv("RAILWAY_ENVIRONMENT"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields without validation errors


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings