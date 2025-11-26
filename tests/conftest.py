"""Pytest configuration and shared fixtures for all tests.

This module provides:
- Test database setup
- Mock services
- Common fixtures
- Test client setup
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return {
        "APP_NAME": "Test AI Agent",
        "APP_VERSION": "0.0.1",
        "ENVIRONMENT": "testing",
        "DEBUG": True,
        "DATABASE_URL": TEST_DATABASE_URL,
        "TRANSACTION_SERVICE_URL": "http://mock-api:8001",
        "OPENAI_API_KEY": "sk-test-key",
        "OPENAI_MODEL": "gpt-4o-mini",
        "SECRET_KEY": "test-secret-key",
    }


@pytest.fixture
def mock_transaction_service():
    """Mock transaction service responses."""
    mock = Mock()
    mock.validate_transaction = AsyncMock(
        return_value={
            "valid": True,
            "message": "Transaction can be processed",
        }
    )
    mock.execute_transaction = AsyncMock(
        return_value={
            "transaction_id": "TXN-12345",
            "status": "completed",
            "phone": "3001234567",
            "amount": 50000,
        }
    )
    mock.get_transaction_status = AsyncMock(
        return_value={
            "transaction_id": "TXN-12345",
            "status": "completed",
        }
    )
    return mock


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing agents."""
    return Mock(
        content="Hola! Soy tu asistente de transacciones. Puedo ayudarte a enviar dinero.",
        additional_kwargs={},
        response_metadata={},
    )


@pytest.fixture
def sample_conversation_state():
    """Sample conversation state for testing."""
    return {
        "messages": [
            {"role": "user", "content": "Hola"},
        ],
        "phone": None,
        "amount": None,
        "needs_confirmation": False,
        "confirmed": False,
        "transaction_id": None,
        "transaction_status": None,
        "error": None,
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "phone": "3001234567",
        "amount": 50000,
        "conversation_id": "conv-123",
    }


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
