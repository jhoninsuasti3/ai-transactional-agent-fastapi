# -*- coding: utf-8 -*-
"""Chat router for API v1 - Simple version without LangGraph agent."""

import uuid
from datetime import datetime

from fastapi import APIRouter
from apps.orchestrator.v1.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

# Simple in-memory conversation storage
conversations = {}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint - simple version without agent."""
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4()}"

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversations[conversation_id].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat(),
    })

    message_lower = request.message.lower()

    # Simple intent detection
    if any(keyword in message_lower for keyword in ["hola", "buenos", "buenas", "hey"]):
        response_text = "Hola! Soy tu asistente de transacciones. Puedo ayudarte a enviar dinero."
        metadata = {"intent": "greeting", "step": "initial"}

    elif any(keyword in message_lower for keyword in ["enviar", "transferir", "mandar"]):
        response_text = "Por supuesto. A que numero de celular deseas enviar dinero?"
        metadata = {"intent": "send_money", "step": "ask_phone"}

    elif any(char.isdigit() for char in request.message) and len("".join(filter(str.isdigit, request.message))) == 10:
        phone = "".join(filter(str.isdigit, request.message))
        response_text = f"Perfecto. Que monto deseas enviar al numero {phone}?"
        metadata = {"intent": "send_money", "step": "ask_amount", "phone": phone}

    else:
        response_text = "Entiendo. En que puedo ayudarte? Puedo asistirte con envios de dinero."
        metadata = {"intent": "unknown", "step": "clarification"}

    conversations[conversation_id].append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.utcnow().isoformat(),
    })

    return ChatResponse(
        response=response_text,
        conversation_id=conversation_id,
        transaction_id=None,
        requires_confirmation=False,
        metadata=metadata,
    )


@router.get("/health")
async def chat_health():
    """Health check for chat router."""
    return {
        "status": "healthy",
        "router": "chat",
        "version": "v1-simple",
        "agent_integrated": False,
        "active_conversations": len(conversations),
    }