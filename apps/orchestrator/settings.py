"""Centralized application settings.

This module provides environment-based configuration management following
the insights_backend pattern for enterprise scalability.
"""

import os
from typing import Literal

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")


class Settings:
    """Application settings with environment-based configuration."""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "AI Transactional Agent")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8001")
    CORS_ALLOW_CREDENTIALS: bool = True

    # Database - Build from individual components or use full URL
    DATABASE_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DATABASE_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_NAME: str = os.getenv("POSTGRES_DB", "transactional_agent")

    # Support both individual vars and full DATABASE_URL
    _database_url_env = os.getenv("DATABASE_URL")
    if _database_url_env and ENVIRONMENT != "test":
        DATABASE_URL: str = _database_url_env
    elif ENVIRONMENT == "test":
        DATABASE_URL = "sqlite:///test.db"
    else:
        DATABASE_URL: str = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))

    # LangChain/OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "transactional-agent")

    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))

    # External Services
    TRANSACTION_SERVICE_URL: str = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8000")
    HTTP_TIMEOUT_CONNECT: float = float(os.getenv("HTTP_TIMEOUT_CONNECT", "5.0"))
    HTTP_TIMEOUT_READ: float = float(os.getenv("HTTP_TIMEOUT_READ", "10.0"))

    # Resilience Patterns
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "console")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Instrumentation
    ENABLE_TELEMETRY: bool = os.getenv("ENABLE_TELEMETRY", "false").lower() == "true"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "transactional-agent-api")

    # Sentry
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return self.DATABASE_URL

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()