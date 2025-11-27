"""Integration tests for health endpoints."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.orchestrator.api.health.router import health_router


@pytest.fixture
def test_app():
    """Create test FastAPI app with health router."""
    app = FastAPI()
    app.include_router(health_router)
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.integration
class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert "database" in data["checks"]
        assert "external_services" in data["checks"]
        assert "timestamp" in data

    def test_liveness_check(self, client):
        """Test liveness check endpoint."""
        response = client.get("/health/live")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_health_check_returns_json(self, client):
        """Test that health check returns JSON content type."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_all_health_endpoints_are_accessible(self, client):
        """Test that all health endpoints are accessible."""
        endpoints = ["/health", "/health/ready", "/health/live"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} should return 200"

    def test_health_timestamp_format(self, client):
        """Test that timestamp is in ISO format."""
        response = client.get("/health")
        data = response.json()

        # Check that timestamp is a string and contains 'T' (ISO format)
        timestamp = data["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp
