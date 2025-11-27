"""Unit tests for confirmation node."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from apps.agents.transactional.nodes.confirmation import confirmation_node
from apps.agents.transactional.state import TransactionalState


@pytest.mark.unit
class TestConfirmationNode:
    """Test suite for confirmation_node."""

    def test_confirmation_with_yes(self):
        """Test confirmation with 'sí' keyword."""
        state: TransactionalState = {
            "messages": [
                HumanMessage(content="Quiero enviar dinero"),
                AIMessage(content="Confirmas?"),
                HumanMessage(content="Sí, confirmo"),
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is True

    def test_confirmation_with_ok(self):
        """Test confirmation with 'ok' keyword."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="Ok, adelante")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is True

    def test_confirmation_with_dale(self):
        """Test confirmation with 'dale' keyword."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="Dale, confirmo")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is True

    def test_cancellation_with_no(self):
        """Test cancellation with 'no' keyword."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="No, mejor no")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False
        assert result["needs_confirmation"] is False

    def test_cancellation_with_cancelar(self):
        """Test cancellation with 'cancelar' keyword."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="Quiero cancelar")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False
        assert result["needs_confirmation"] is False

    def test_no_confirmation_keyword(self):
        """Test message without confirmation keyword."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="Cuéntame más")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False

    def test_empty_messages(self):
        """Test with empty messages."""
        state: TransactionalState = {
            "messages": [],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False

    def test_only_ai_messages(self):
        """Test with only AI messages (no human messages)."""
        state: TransactionalState = {
            "messages": [AIMessage(content="Hola"), AIMessage(content="¿Confirmas?")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False

    def test_multiple_human_messages_uses_last(self):
        """Test that it uses the last human message for confirmation."""
        state: TransactionalState = {
            "messages": [
                HumanMessage(content="Sí"),
                AIMessage(content="Confirmación recibida"),
                HumanMessage(content="No, espera, cancelar"),
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is False
        assert result["needs_confirmation"] is False

    def test_case_insensitive_keywords(self):
        """Test that keywords are case insensitive."""
        state: TransactionalState = {
            "messages": [HumanMessage(content="SI, CONFIRMO")],
            "phone": None,
            "amount": None,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = confirmation_node(state)
        assert result["confirmed"] is True
