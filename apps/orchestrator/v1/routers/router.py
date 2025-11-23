"""API V1 router aggregation."""

from fastapi import APIRouter

# Import routers here as they are created
# from apps.apps.v1.routers.chat import chat_router
# from apps.apps.v1.routers.conversations import conversations_router
# from apps.apps.v1.routers.transactions import transactions_router

api_v1_router = APIRouter()

# Include routers
# api_v1_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
# api_v1_router.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
# api_v1_router.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])


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
