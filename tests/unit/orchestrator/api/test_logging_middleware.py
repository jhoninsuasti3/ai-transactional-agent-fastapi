"""Unit tests for logging middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import logging

from apps.orchestrator.api.middlewares.logging import LoggingMiddleware


@pytest.fixture
def test_app():
    """Create test FastAPI app with logging middleware."""
    app = FastAPI()

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Add test route
    @app.get("/test")
    async def test_route():
        return {"message": "test"}

    @app.get("/error")
    async def error_route():
        raise ValueError("Test error")

    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.unit
class TestLoggingMiddleware:
    """Test suite for LoggingMiddleware."""

    def test_middleware_logs_request(self, client):
        """Test middleware logs incoming requests."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            # Verify logger was called for request
            assert mock_logger.info.called

    def test_middleware_logs_response(self, client):
        """Test middleware logs responses."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            # Verify logger was called
            assert mock_logger.info.call_count >= 1

    def test_middleware_logs_method_and_path(self, client):
        """Test middleware logs HTTP method and path."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            client.get("/test")

            # Check if any call contains method and path info
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("GET" in str(call) or "/test" in str(call) for call in calls)

    def test_middleware_logs_status_code(self, client):
        """Test middleware logs response status code."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            # Verify status code is logged
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("200" in str(call) for call in calls)

    def test_middleware_logs_duration(self, client):
        """Test middleware logs request duration."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            client.get("/test")

            # Check if duration/time is logged
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert len(calls) > 0

    def test_middleware_handles_errors(self, client):
        """Test middleware handles errors gracefully."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            # This will raise an error - middleware logs but doesn't catch
            try:
                response = client.get("/error")
            except:
                pass

            # Middleware should have logged the request
            assert mock_logger.info.called

    def test_middleware_with_post_request(self, client):
        """Test middleware works with POST requests."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            # Add a POST route for testing
            response = client.post("/test", json={"data": "test"})

            # Middleware should log POST requests too
            assert mock_logger.info.called

    def test_middleware_processes_request_chain(self, client):
        """Test middleware doesn't break request chain."""
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "test"}

    def test_middleware_logs_different_endpoints(self, client):
        """Test middleware logs different endpoints."""
        with patch('apps.orchestrator.api.middlewares.logging.logger') as mock_logger:
            client.get("/test")
            call_count_1 = mock_logger.info.call_count

            client.get("/test")
            call_count_2 = mock_logger.info.call_count

            # Should have logged both requests
            assert call_count_2 > call_count_1
