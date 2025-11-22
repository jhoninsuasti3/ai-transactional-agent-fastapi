"""Domain ports (interfaces) - Hexagonal Architecture.

These define the contracts that infrastructure adapters must implement.
"""

from apps.domain.ports.transaction_port import TransactionPort
from apps.domain.ports.repository_port import (
    ConversationRepository,
    TransactionRepository,
)

__all__ = [
    "TransactionPort",
    "ConversationRepository",
    "TransactionRepository",
]