"""API V1 router aggregation."""

from fastapi import APIRouter

from apps.orchestrator.v1.routers.chat import router as chat_router
from apps.orchestrator.v1.routers.conversations import router as conversations_router
from apps.orchestrator.v1.routers.transactions import router as transactions_router

api_v1_router = APIRouter()

# Include routers
api_v1_router.include_router(chat_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(transactions_router)


@api_v1_router.get("/")
async def v1_root() -> dict:
    """API V1 root endpoint.

    Returns:
        dict: API v1 information
    """
    return {
        "version": "1.0",
        "status": "active",
        "endpoints": {
            "chat": "/chat",
            "conversations": "/conversations",
            "transactions": "/transactions",
        },
    }
