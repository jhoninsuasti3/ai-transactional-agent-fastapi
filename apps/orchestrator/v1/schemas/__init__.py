"""Pydantic schemas for API v1."""

from apps.orchestrator.v1.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConfirmationRequest,
    ConfirmationResponse,
)
from apps.orchestrator.v1.schemas.common import (
    BaseResponse,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    PaginationParams,
)
from apps.orchestrator.v1.schemas.conversation import (
    ConversationDetail,
    ConversationStatus,
    ConversationSummary,
    Message,
    MessageRole,
)
from apps.orchestrator.v1.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionResponse,
    TransactionStatus,
)

__all__ = [
    # Chat
    "ChatRequest",
    "ChatResponse",
    "ConfirmationRequest",
    "ConfirmationResponse",
    # Common
    "BaseResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "PaginationParams",
    # Conversation
    "ConversationDetail",
    "ConversationStatus",
    "ConversationSummary",
    "Message",
    "MessageRole",
    # Transaction
    "TransactionCreate",
    "TransactionDetail",
    "TransactionResponse",
    "TransactionStatus",
]
