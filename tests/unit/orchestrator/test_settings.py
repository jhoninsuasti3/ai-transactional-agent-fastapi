"""Unit tests for orchestrator settings."""

import pytest
from pydantic import ValidationError

from apps.orchestrator.settings import Settings


@pytest.mark.unit
class TestSettings:
    """Test suite for application settings."""

    def test_settings_loads_from_env(self):
        """Test settings loads from environment variables."""
        settings = Settings()
        assert settings is not None
        assert settings.APP_NAME is not None
        assert settings.APP_VERSION is not None

    def test_settings_database_url_construction(self):
        """Test database URL is correctly constructed."""
        settings = Settings()
        assert "postgresql" in settings.database_url_str

    def test_settings_log_level_default(self):
        """Test log level has a default value."""
        settings = Settings()
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]

    def test_settings_environment_default(self):
        """Test environment has a default value."""
        settings = Settings()
        assert settings.ENVIRONMENT in ["development", "production", "testing"]

    def test_settings_app_version(self):
        """Test APP version is set."""
        settings = Settings()
        assert settings.APP_VERSION is not None

    def test_settings_cors_origins(self):
        """Test CORS origins is configured."""
        settings = Settings()
        assert settings.CORS_ORIGINS is not None
        assert isinstance(settings.CORS_ORIGINS, str)

    def test_settings_database_pool_size(self):
        """Test database pool size is configured."""
        settings = Settings()
        assert settings.DATABASE_POOL_SIZE > 0

    def test_settings_database_max_overflow(self):
        """Test database max overflow is configured."""
        settings = Settings()
        assert settings.DATABASE_MAX_OVERFLOW >= 0
