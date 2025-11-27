"""Unit tests for request ID middleware."""

import uuid

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from apps.orchestrator.api.middlewares.request_id import RequestIDMiddleware


@pytest.fixture
def test_app():
    """Create test FastAPI app with request ID middleware."""
    app = FastAPI()

    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)

    # Add test route that returns request ID
    @app.get("/test")
    async def test_route(request: Request):
        request_id = getattr(request.state, "request_id", None)
        return {"message": "test", "request_id": request_id}

    @app.get("/echo-headers")
    async def echo_headers(request: Request):
        return {"x_request_id": request.headers.get("X-Request-ID")}

    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.unit
class TestRequestIDMiddleware:
    """Test suite for RequestIDMiddleware."""

    def test_middleware_adds_request_id(self, client):
        """Test middleware adds request ID to response headers."""
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    def test_request_id_is_valid_uuid(self, client):
        """Test generated request ID is a valid UUID."""
        response = client.get("/test")

        request_id = response.headers.get("X-Request-ID")
        assert request_id is not None

        # Verify it's a valid UUID
        try:
            uuid.UUID(request_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False

        assert is_valid_uuid

    def test_request_id_unique_per_request(self, client):
        """Test each request gets a unique request ID."""
        response1 = client.get("/test")
        response2 = client.get("/test")

        request_id1 = response1.headers.get("X-Request-ID")
        request_id2 = response2.headers.get("X-Request-ID")

        assert request_id1 != request_id2

    def test_middleware_uses_existing_request_id(self, client):
        """Test middleware uses existing X-Request-ID header if provided."""
        existing_id = str(uuid.uuid4())

        response = client.get("/test", headers={"X-Request-ID": existing_id})

        returned_id = response.headers.get("X-Request-ID")
        assert returned_id == existing_id

    def test_request_id_attached_to_state(self, client):
        """Test request ID is attached to request state."""
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()

        # Check if request_id was accessible in the route
        assert data.get("request_id") is not None

    def test_request_id_matches_header_and_state(self, client):
        """Test request ID in header matches state."""
        response = client.get("/test")

        header_id = response.headers.get("X-Request-ID")
        state_id = response.json().get("request_id")

        assert header_id == state_id

    def test_middleware_with_post_request(self, client):
        """Test middleware works with POST requests."""
        response = client.post("/test", json={"data": "test"})

        assert "X-Request-ID" in response.headers
        request_id = response.headers.get("X-Request-ID")

        # Verify it's a valid UUID
        try:
            uuid.UUID(request_id)
            is_valid = True
        except ValueError:
            is_valid = False

        assert is_valid

    def test_middleware_preserves_response(self, client):
        """Test middleware doesn't modify response body."""
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "test"

    def test_multiple_requests_have_request_ids(self, client):
        """Test multiple requests all get request IDs."""
        request_ids = set()

        for _ in range(5):
            response = client.get("/test")
            request_id = response.headers.get("X-Request-ID")
            request_ids.add(request_id)

        # All request IDs should be unique
        assert len(request_ids) == 5

    def test_request_id_with_custom_header(self, client):
        """Test providing custom request ID in header."""
        custom_ids = [str(uuid.uuid4()) for _ in range(3)]

        for custom_id in custom_ids:
            response = client.get("/test", headers={"X-Request-ID": custom_id})
            returned_id = response.headers.get("X-Request-ID")
            assert returned_id == custom_id
