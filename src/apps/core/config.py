"""Application configuration using Pydantic Settings.

Loads configuration from environment variables with validation.
"""

from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = Field(
        default="AI Transactional Agent",
        description="Application name",
    )
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment",
    )

    # API
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_WORKERS: int = Field(default=1, description="Number of workers")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials",
    )

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/transactional_agent",
        description="PostgreSQL connection string (async)",
    )
    DATABASE_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size",
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        description="Max overflow connections",
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries (debug)",
    )

    # OpenAI (for LangGraph agent in production)
    OPENAI_API_KEY: str = Field(
        ...,  # Required
        description="OpenAI API key for the agent",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use",
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature",
    )
    OPENAI_MAX_TOKENS: int = Field(
        default=500,
        description="Max tokens per response",
    )

    # Anthropic (for development with Claude Code)
    ANTHROPIC_API_KEY: str | None = Field(
        default=None,
        description="Anthropic API key (optional, for development)",
    )

    # Transaction Service (Mock API)
    TRANSACTION_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        description="Base URL for transaction service",
    )

    # HTTP Client Timeouts
    HTTP_TIMEOUT_CONNECT: float = Field(
        default=5.0,
        description="HTTP connection timeout (seconds)",
    )
    HTTP_TIMEOUT_READ: float = Field(
        default=10.0,
        description="HTTP read timeout (seconds)",
    )

    # Retry Pattern
    MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts",
    )
    RETRY_BACKOFF_BASE: float = Field(
        default=1.0,
        description="Base backoff time (seconds)",
    )
    RETRY_BACKOFF_MAX: float = Field(
        default=4.0,
        description="Max backoff time (seconds)",
    )

    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(
        default=5,
        ge=1,
        description="Failures before circuit opens",
    )
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = Field(
        default=60,
        ge=1,
        description="Seconds before attempting reset",
    )

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    LOG_FORMAT: Literal["json", "console"] = Field(
        default="json",
        description="Log output format",
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT and encryption",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration (minutes)",
    )

    # LangGraph
    LANGGRAPH_CHECKPOINT_DB: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/transactional_agent",
        description="PostgreSQL connection for LangGraph checkpointing (sync)",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str | PostgresDsn) -> str:
        """Ensure DATABASE_URL is a string."""
        if isinstance(v, str):
            return v
        return str(v)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.DATABASE_URL)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()


# Validation on import
def validate_settings() -> None:
    """Validate critical settings on startup."""
    if settings.is_production and settings.SECRET_KEY == "your-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be changed in production")

    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")


# Run validation
if __name__ != "__main__":
    validate_settings()