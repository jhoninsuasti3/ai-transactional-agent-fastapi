"""Domain ports (interfaces) - Hexagonal Architecture.

These define the contracts that infrastructure adapters must implement.
"""

from src.apps.domain.ports.transaction_port import TransactionPort
from src.apps.domain.ports.repository_port import (
    ConversationRepository,
    TransactionRepository,
)

__all__ = [
    "TransactionPort",
    "ConversationRepository",
    "TransactionRepository",
]