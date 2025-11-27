"""Unit tests for TransactionAPIClient HTTP client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from apps.agents.transactional.tools.http_client import TransactionAPIClient, transaction_client


@pytest.mark.unit
class TestTransactionAPIClient:
    """Test suite for TransactionAPIClient."""

    def test_client_initialization(self):
        """Test client initializes with correct settings."""
        client = TransactionAPIClient()

        assert client.base_url is not None
        assert client.timeout is not None
        assert isinstance(client.timeout, httpx.Timeout)

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_make_request_success_post(self, mock_client_class):
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()
        result = client._make_request("POST", "/test", json={"data": "value"})

        assert result == {"result": "success"}
        mock_client_instance.request.assert_called_once_with(
            "POST", f"{client.base_url}/test", json={"data": "value"}
        )

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_make_request_success_get(self, mock_client_class):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "status": "active"}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()
        result = client._make_request("GET", "/status/123")

        assert result == {"id": "123", "status": "active"}
        mock_client_instance.request.assert_called_once()

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_make_request_http_status_error(self, mock_client_class):
        """Test request with HTTP status error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()

        with pytest.raises(httpx.HTTPStatusError):
            client._make_request("POST", "/fail")

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_make_request_timeout(self, mock_client_class):
        """Test request with timeout."""
        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.TimeoutException("Timeout")
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()

        with pytest.raises(httpx.TimeoutException):
            client._make_request("GET", "/slow")

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_make_request_network_error(self, mock_client_class):
        """Test request with network error."""
        mock_client_instance = MagicMock()
        mock_client_instance.request.side_effect = httpx.RequestError("Connection failed")
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()

        with pytest.raises(httpx.RequestError):
            client._make_request("POST", "/unavailable")

    @patch.object(TransactionAPIClient, "_make_request")
    def test_post_method(self, mock_make_request):
        """Test post method calls _make_request with correct arguments."""
        mock_make_request.return_value = {"transaction_id": "TXN-123"}

        client = TransactionAPIClient()
        result = client.post("/transactions", json={"amount": 50000})

        assert result == {"transaction_id": "TXN-123"}
        mock_make_request.assert_called_once_with("POST", "/transactions", json={"amount": 50000})

    @patch.object(TransactionAPIClient, "_make_request")
    def test_get_method(self, mock_make_request):
        """Test get method calls _make_request with correct arguments."""
        mock_make_request.return_value = {"status": "completed"}

        client = TransactionAPIClient()
        result = client.get("/transactions/TXN-123")

        assert result == {"status": "completed"}
        mock_make_request.assert_called_once_with("GET", "/transactions/TXN-123")

    def test_singleton_instance_exists(self):
        """Test that singleton transaction_client instance exists."""
        assert transaction_client is not None
        assert isinstance(transaction_client, TransactionAPIClient)

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_timeout_configuration(self, mock_client_class):
        """Test that timeout is configured correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()
        client._make_request("GET", "/test")

        # Verify Client was created with timeout
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == client.timeout

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_response_raises_for_status(self, mock_client_class):
        """Test that raise_for_status is called on response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()
        client._make_request("POST", "/test", json={})

        mock_response.raise_for_status.assert_called_once()

    @patch("apps.agents.transactional.tools.http_client.httpx.Client")
    def test_request_with_json_body(self, mock_client_class):
        """Test request properly passes JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}

        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None

        mock_client_class.return_value = mock_client_instance

        client = TransactionAPIClient()
        json_data = {"phone": "3001234567", "amount": 50000}
        result = client._make_request("POST", "/validate", json=json_data)

        assert result == {"created": True}
        call_args = mock_client_instance.request.call_args
        assert call_args[1]["json"] == json_data
