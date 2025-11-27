"""Base entity classes for domain models.

Provides base classes for entities and value objects following DDD principles.
"""

from datetime import UTC, datetime
from typing import Any


class Entity:
    """Base class for domain entities.

    An entity has a unique identity that persists through changes.
    Two entities are equal if they have the same ID, regardless of their attributes.
    """

    def __init__(self, id: int | None = None) -> None:  # noqa: A002
        """Initialize entity.

        Args:
            id: Unique identifier (None for new entities)
        """
        self.id = id

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID.

        Args:
            other: Other object to compare

        Returns:
            bool: True if same entity (same ID)
        """
        if not isinstance(other, self.__class__):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID.

        Returns:
            int: Hash value
        """
        return hash(self.id) if self.id is not None else hash(id(self))

    def __repr__(self) -> str:
        """String representation.

        Returns:
            str: Entity representation
        """
        return f"{self.__class__.__name__}(id={self.id})"


class AggregateRoot(Entity):
    """Base class for aggregate roots.

    An aggregate root is an entity that is the entry point to an aggregate.
    All operations on the aggregate must go through the aggregate root.
    """

    def __init__(self, id: int | None = None) -> None:  # noqa: A002
        """Initialize aggregate root.

        Args:
            id: Unique identifier (None for new aggregates)
        """
        super().__init__(id)
        self._domain_events: list[Any] = []

    def add_domain_event(self, event: Any) -> None:
        """Add a domain event.

        Args:
            event: Domain event to add
        """
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    @property
    def domain_events(self) -> list[Any]:
        """Get domain events.

        Returns:
            list: List of domain events
        """
        return self._domain_events.copy()


class ValueObject:
    """Base class for value objects.

    A value object has no unique identity. It is defined entirely by its attributes.
    Two value objects are equal if all their attributes are equal.
    Value objects should be immutable.
    """

    def __eq__(self, other: object) -> bool:
        """Check equality based on all attributes.

        Args:
            other: Other object to compare

        Returns:
            bool: True if all attributes are equal
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on all attributes.

        Returns:
            int: Hash value
        """
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """String representation.

        Returns:
            str: Value object representation
        """
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class Auditable:
    """Mixin for entities that need audit timestamps."""

    def __init__(self) -> None:
        """Initialize auditable entity."""
        self.created_at: datetime | None = None
        self.updated_at: datetime | None = None

    def mark_created(self, timestamp: datetime | None = None) -> None:
        """Mark entity as created.

        Args:
            timestamp: Creation timestamp (defaults to now)
        """
        self.created_at = timestamp or datetime.now(UTC)
        self.updated_at = self.created_at

    def mark_updated(self, timestamp: datetime | None = None) -> None:
        """Mark entity as updated.

        Args:
            timestamp: Update timestamp (defaults to now)
        """
        self.updated_at = timestamp or datetime.now(UTC)
