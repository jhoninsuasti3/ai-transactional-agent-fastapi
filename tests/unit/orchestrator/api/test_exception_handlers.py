"""Unit tests for exception handlers."""

import pytest
from fastapi import FastAPI, HTTPException as FastAPIHTTPException
from fastapi.testclient import TestClient

from apps.orchestrator.core.exceptions import (
    AppException,
    ExternalServiceError,
    HTTPException,
    NotFoundError,
)
from apps.orchestrator.domain.exceptions.base import DomainException
from apps.orchestrator.api.exception_handlers.handlers import register_exception_handlers


@pytest.fixture
def test_app():
    """Create test FastAPI app with exception handlers."""
    app = FastAPI()

    # Register exception handlers
    register_exception_handlers(app)

    # Add test routes that raise exceptions
    @app.get("/app-exception")
    async def raise_app_exception():
        raise AppException("App error", details={"code": "APP001"})

    @app.get("/domain-exception")
    async def raise_domain_exception():
        raise DomainException("Domain error")

    @app.get("/external-service-error")
    async def raise_external_service_error():
        raise ExternalServiceError("Service unavailable", details={"service": "payment"})

    @app.get("/not-found-error")
    async def raise_not_found_error():
        raise NotFoundError("Transaction", "TXN-12345")

    @app.get("/http-exception")
    async def raise_http_exception():
        raise HTTPException(status_code=400, message="Bad request")

    @app.get("/general-exception")
    async def raise_general_exception():
        raise ValueError("Unexpected error")

    @app.get("/fastapi-http-exception")
    async def raise_fastapi_http_exception():
        raise FastAPIHTTPException(status_code=400, detail="FastAPI bad request")

    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app, raise_server_exceptions=False)


@pytest.mark.unit
class TestExceptionHandlers:
    """Test suite for exception handlers."""

    def test_app_exception_handler(self, client):
        """Test AppException is handled correctly."""
        response = client.get("/app-exception")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"] == "Internal server error"

    def test_domain_exception_handler(self, client):
        """Test DomainException is handled correctly."""
        response = client.get("/domain-exception")

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Domain error"
        assert "timestamp" in data

    def test_external_service_error_handler(self, client):
        """Test ExternalServiceError is handled correctly."""
        response = client.get("/external-service-error")

        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "External service temporarily unavailable"
        assert data["message"] == "Service unavailable"
        assert data["details"]["service"] == "payment"

    def test_not_found_error_handler(self, client):
        """Test NotFoundError is handled correctly."""
        response = client.get("/not-found-error")

        assert response.status_code == 404
        data = response.json()
        assert "Transaction" in data["error"]
        assert "TXN-12345" in data["error"]

    def test_http_exception_handler(self, client):
        """Test HTTPException is handled correctly."""
        response = client.get("/http-exception")

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Bad request"

    def test_general_exception_handler(self, client):
        """Test general Exception is handled correctly."""
        response = client.get("/general-exception")

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Internal server error"

    def test_exception_handler_includes_timestamp(self, client):
        """Test all exception handlers include timestamp field."""
        endpoints = [
            "/app-exception",
            "/domain-exception",
            "/external-service-error",
            "/not-found-error",
            "/http-exception",
            "/general-exception",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            assert "timestamp" in data, f"Missing timestamp field in {endpoint}"

    def test_exception_handler_status_codes(self, client):
        """Test exception handlers return correct status codes."""
        test_cases = [
            ("/domain-exception", 400),
            ("/not-found-error", 404),
            ("/app-exception", 500),
            ("/external-service-error", 503),
            ("/http-exception", 400),
            ("/general-exception", 500),
        ]

        for endpoint, expected_status in test_cases:
            response = client.get(endpoint)
            assert response.status_code == expected_status, \
                f"{endpoint} returned {response.status_code}, expected {expected_status}"

    def test_exception_handler_preserves_details(self, client):
        """Test exception handlers preserve details dict."""
        response = client.get("/external-service-error")

        data = response.json()
        assert "details" in data
        assert data["details"]["service"] == "payment"

    def test_exception_handler_json_response(self, client):
        """Test exception handlers return valid JSON."""
        endpoints = [
            "/app-exception",
            "/domain-exception",
            "/external-service-error",
            "/not-found-error",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not raise JSONDecodeError
            data = response.json()
            assert isinstance(data, dict)

    def test_domain_exception_with_details(self, client):
        """Test domain exception with details is handled correctly."""
        response = client.get("/domain-exception")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "details" in data

    def test_not_found_error_includes_details(self, client):
        """Test NotFoundError includes transaction details."""
        response = client.get("/not-found-error")

        data = response.json()
        assert response.status_code == 404
        assert data["details"]["identifier"] == "TXN-12345"
        assert data["details"]["resource"] == "Transaction"

    def test_external_service_error_structure(self, client):
        """Test ExternalServiceError has correct response structure."""
        response = client.get("/external-service-error")

        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "details" in data
        assert "timestamp" in data
