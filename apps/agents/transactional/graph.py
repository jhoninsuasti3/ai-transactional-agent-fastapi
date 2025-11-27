"""LangGraph agent for transactional money transfers.

Defines the state machine graph with nodes and conditional routing.
"""

import structlog
from langgraph.graph import END, StateGraph

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
    """Route after conversation: extract or end if simple conversation."""
    import re

    logger.info(
        "should_extract_called",
        phone=state.get("phone"),
        amount=state.get("amount"),
        needs_confirmation=state.get("needs_confirmation"),
        message_count=len(state.get("messages", [])),
    )

    # If we already have both phone and amount, go validate
    if state.get("phone") and state.get("amount"):
        logger.info("should_extract_decision", decision="validate", reason="has_phone_and_amount")
        return "validate"

    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        logger.info("should_extract_decision", decision="END", reason="no_messages")
        return END

    last_user_msg = None
    for msg in reversed(messages):
        # Check for HumanMessage (LangChain message type)
        if hasattr(msg, "type") and msg.type == "human":
            # Handle both string and list content
            content = msg.content
            if isinstance(content, list):
                # If content is a list, join all text parts
                content = " ".join(str(item) for item in content)
            elif not isinstance(content, str):
                content = str(content)

            last_user_msg = content
            break

    if not last_user_msg:
        logger.info("should_extract_decision", decision="END", reason="no_user_message")
        return END

    last_user_msg.lower()

    # Check if message contains numbers (phone or amount)
    has_phone_pattern = bool(re.search(r"\b3\d{9}\b", last_user_msg))
    has_amount_pattern = bool(re.search(r"\$?\d+", last_user_msg))

    # Only go to extract if we have actual data to extract (numbers)
    if has_phone_pattern or has_amount_pattern:
        logger.info(
            "should_extract_decision",
            decision="extract",
            reason="found_data_pattern",
            msg=last_user_msg[:50],
        )
        return "extract"

    # No data to extract - just end this turn
    logger.info("should_extract_decision", decision="END", reason="no_data_in_message")
    return END


def should_validate(state: TransactionalState) -> str:
    """Route after extraction: validate if we have data, else END (let user provide more info)."""
    logger.info("should_validate_called", phone=state.get("phone"), amount=state.get("amount"))

    if state.get("phone") and state.get("amount"):
        logger.info("should_validate_decision", decision="validate")
        return "validate"

    # If extraction didn't find complete data, END the current turn
    # The user will provide more info in the next message
    logger.info("should_validate_decision", decision="END", reason="missing_data")
    return END


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


def create_graph(checkpointer=None):
    """Create the LangGraph state machine.

    Args:
        checkpointer: Optional checkpointer for state persistence

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
            END: END,
        },
    )

    graph.add_conditional_edges(
        "extract",
        should_validate,
        {
            "validate": "validate",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "validate",
        should_confirm,
        {
            "confirmation": "confirmation",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "confirmation",
        should_execute,
        {
            "transaction": "transaction",
            END: END,
        },
    )

    # Transaction is terminal
    graph.add_edge("transaction", END)

    logger.info("graph_created", nodes=5, edges=5, has_checkpointer=checkpointer is not None)

    return graph.compile(checkpointer=checkpointer)


# Create base graph without checkpointer (will be created per-request with checkpointer)
def get_agent(checkpointer=None):
    """Get compiled agent with optional checkpointer.

    Args:
        checkpointer: Optional checkpointer for state persistence

    Returns:
        Compiled agent
    """
    return create_graph(checkpointer=checkpointer)
