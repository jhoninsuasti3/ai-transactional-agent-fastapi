"""LangGraph agent for transactional money transfers.

Defines the state machine graph with nodes and conditional routing.
"""

import structlog
from langgraph.graph import StateGraph, END

from apps.agents.transactional.nodes import (
    confirmation_node,
    conversation_node,
    extractor_node,
    transaction_node,
    validator_node,
)
from apps.agents.transactional.state import TransactionalState

logger = structlog.get_logger(__name__)


def should_extract(state: TransactionalState) -> str:
    """Route after conversation: extract or continue conversation."""
    # Check if we have both phone and amount
    if state.get("phone") and state.get("amount"):
        return "validate"
    return "extract"


def should_validate(state: TransactionalState) -> str:
    """Route after extraction: validate if we have data, else continue conversation."""
    if state.get("phone") and state.get("amount"):
        return "validate"
    return "conversation"


def should_confirm(state: TransactionalState) -> str:
    """Route after validation: ask for confirmation or end."""
    if state.get("needs_confirmation"):
        return "confirmation"
    return END


def should_execute(state: TransactionalState) -> str:
    """Route after confirmation: execute if confirmed, else end."""
    if state.get("confirmed"):
        return "transaction"
    return END


def create_graph() -> StateGraph:
    """Create the LangGraph state machine.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    graph = StateGraph(TransactionalState)

    # Add nodes
    graph.add_node("conversation", conversation_node)
    graph.add_node("extract", extractor_node)
    graph.add_node("validate", validator_node)
    graph.add_node("confirmation", confirmation_node)
    graph.add_node("transaction", transaction_node)

    # Set entry point
    graph.set_entry_point("conversation")

    # Add edges with conditional routing
    graph.add_conditional_edges(
        "conversation",
        should_extract,
        {
            "extract": "extract",
            "validate": "validate",
        }
    )

    graph.add_conditional_edges(
        "extract",
        should_validate,
        {
            "validate": "validate",
            "conversation": "conversation",
        }
    )

    graph.add_conditional_edges(
        "validate",
        should_confirm,
        {
            "confirmation": "confirmation",
            END: END,
        }
    )

    graph.add_conditional_edges(
        "confirmation",
        should_execute,
        {
            "transaction": "transaction",
            END: END,
        }
    )

    # Transaction is terminal
    graph.add_edge("transaction", END)

    logger.info("graph_created", nodes=5, edges=5)

    return graph.compile()


# Create singleton instance
agent = create_graph()
