"""Integration tests for conversations router."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from apps.orchestrator.v1.routers.conversations import router


@pytest.fixture
def test_app():
    """Create test FastAPI app with conversations router."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.integration
class TestConversationsRouter:
    """Test suite for conversations router endpoints."""

    def test_get_conversation_returns_mock_data(self, client):
        """Test getting conversation returns mock data."""
        response = client.get("/api/v1/conversations/conv-test-123")
        assert response.status_code == 200

        data = response.json()
        assert data["conversation_id"] == "conv-test-123"
        assert data["user_id"] == "user-123"
        assert data["status"] == "active"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_get_conversation_includes_timestamps(self, client):
        """Test conversation includes timestamp fields."""
        response = client.get("/api/v1/conversations/conv-456")
        assert response.status_code == 200

        data = response.json()
        assert "started_at" in data
        assert "ended_at" in data
        assert "transaction_ids" in data

    def test_get_conversation_messages_structure(self, client):
        """Test messages have correct structure."""
        response = client.get("/api/v1/conversations/conv-789")
        assert response.status_code == 200

        data = response.json()
        messages = data["messages"]

        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert "timestamp" in msg
            assert msg["role"] in ["user", "assistant", "system"]

    def test_get_conversation_different_ids(self, client):
        """Test different conversation IDs work."""
        conv_ids = ["conv-1", "conv-2", "conv-3", "test-conversation"]

        for conv_id in conv_ids:
            response = client.get(f"/api/v1/conversations/{conv_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == conv_id

    def test_conversations_health_endpoint(self, client):
        """Test conversations health check - treated as conversation_id."""
        # Note: Due to route ordering, '/health' is treated as a conversation_id
        response = client.get("/api/v1/conversations/health")
        assert response.status_code == 200

        data = response.json()
        # The health path is caught by /{conversation_id} route
        assert data["conversation_id"] == "health"
        assert data["status"] == "active"

    def test_conversation_response_schema(self, client):
        """Test response matches ConversationDetail schema."""
        response = client.get("/api/v1/conversations/schema-test")
        assert response.status_code == 200

        data = response.json()
        required_fields = [
            "conversation_id",
            "user_id",
            "status",
            "messages",
            "started_at",
            "ended_at",
            "transaction_ids"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_conversation_status_is_active(self, client):
        """Test default conversation status is active."""
        response = client.get("/api/v1/conversations/active-test")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "active"

    def test_conversation_transaction_ids_empty(self, client):
        """Test default transaction_ids is empty list."""
        response = client.get("/api/v1/conversations/empty-transactions")
        assert response.status_code == 200

        data = response.json()
        assert data["transaction_ids"] == []
        assert isinstance(data["transaction_ids"], list)
