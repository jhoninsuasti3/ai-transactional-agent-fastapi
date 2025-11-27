"""Transactional Agent - Main graph builder.

This module creates the LangGraph agent for handling money transfer transactions
through natural language conversation.
"""

from typing import Any

from langgraph.graph import END, START, CompiledStateGraph, StateGraph

from apps.agents.transactional.nodes.conversation import conversation_node
from apps.agents.transactional.nodes.extractor import extractor_node
from apps.agents.transactional.nodes.transaction import transaction_node
from apps.agents.transactional.nodes.validator import validator_node
from apps.agents.transactional.routes.intent.route import intent_route
from apps.agents.transactional.routes.validation.route import validation_route
from apps.agents.transactional.state import TransactionalState


def create_transactional_agent(config: dict[str, Any] | None = None) -> CompiledStateGraph:
    """Create the transactional agent graph.

    This function builds a LangGraph agent that handles the full transaction flow:
    1. Extract intent and entities from user message
    2. Route based on intent (conversation, transaction, etc.)
    3. Validate transaction details
    4. Execute transaction if validated
    5. Return to conversation

    Args:
        config: Configuration dict with optional:
            - checkpointer: AsyncPostgresSaver for persistence
            - llm: LLM instance to use
            - transaction_client: External transaction service client

    Returns:
        Compiled LangGraph agent

    Example:
        >>> from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        >>> checkpointer = AsyncPostgresSaver(conn_string="postgresql://...")
        >>> agent = create_transactional_agent({"checkpointer": checkpointer})
        >>> result = await agent.ainvoke(
        ...     {"messages": [{"role": "user", "content": "Send $100 to 555-1234"}]},
        ...     config={"configurable": {"thread_id": "user-123"}}
        ... )
    """
    config = config or {}
    checkpointer = config.get("checkpointer", None)

    # Build the graph
    builder = StateGraph(TransactionalState)

    # Add nodes
    builder.add_node("extractor", extractor_node)
    builder.add_node("conversation", conversation_node)
    builder.add_node("validator", validator_node)
    builder.add_node("transaction", transaction_node)

    # Define edges
    builder.add_edge(START, "extractor")

    # Route based on extracted intent
    builder.add_conditional_edges(
        "extractor",
        intent_route,
        {
            "conversation": "conversation",
            "transaction": "validator",
        },
    )

    # Conversation flow
    builder.add_edge("conversation", END)

    # Transaction validation flow
    builder.add_conditional_edges(
        "validator",
        validation_route,
        {
            "valid": "transaction",
            "invalid": "conversation",
        },
    )

    # Transaction execution flow
    builder.add_edge("transaction", "conversation")

    # Compile the graph
    return builder.compile(checkpointer=checkpointer)
