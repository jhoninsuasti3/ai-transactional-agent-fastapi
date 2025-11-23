"""Centralized application settings.

This module provides environment-based configuration management following
the insights_backend pattern for enterprise scalability.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AI Transactional Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = Field(default=False)

    # API
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_PREFIX: str = Field(default="/api")

    # CORS
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = True

    # Database
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="transactional_agent")
    DATABASE_USER: str = Field(default="postgres")
    DATABASE_PASSWORD: str = Field(default="postgres")
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)

    # LangChain/OpenAI
    OPENAI_API_KEY: str = Field(default="")
    LANGCHAIN_API_KEY: str = Field(default="")
    LANGCHAIN_TRACING_V2: bool = Field(default=False)
    LANGCHAIN_PROJECT: str = Field(default="transactional-agent")

    # LLM Configuration
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    LLM_TEMPERATURE: float = Field(default=0.0)
    LLM_MAX_TOKENS: int = Field(default=1000)

    # External Services
    TRANSACTION_SERVICE_URL: str = Field(default="http://localhost:8001")
    HTTP_TIMEOUT_CONNECT: float = Field(default=5.0)
    HTTP_TIMEOUT_READ: float = Field(default=10.0)

    # Resilience Patterns
    MAX_RETRIES: int = Field(default=3)
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5)
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = Field(default=60)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: Literal["json", "console"] = Field(default="console")

    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Instrumentation
    ENABLE_TELEMETRY: bool = Field(default=False)
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="")
    OTEL_SERVICE_NAME: str = Field(default="transactional-agent-api")

    # Sentry
    SENTRY_DSN: str = Field(default="")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=1.0)

    @property
    def database_url(self) -> PostgresDsn:
        """Build async PostgreSQL DSN."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=self.DATABASE_NAME,
        )

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.database_url)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate and normalize environment."""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Cached application settings
    """
    return Settings()


# Global settings instance
settings = get_settings()