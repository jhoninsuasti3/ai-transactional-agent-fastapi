# -*- coding: utf-8 -*-
"""Chat schemas for API v1."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_id: str | None = Field(None, description="Conversation ID")
    user_id: str = Field(..., description="User identifier")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    response: str = Field(..., description="Agent response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    transaction_id: str | None = Field(None, description="Transaction ID if initiated")
    requires_confirmation: bool = Field(default=False, description="Requires confirmation")
    metadata: dict | None = Field(None, description="Additional metadata")


class ConfirmationRequest(BaseModel):
    """Request schema for transaction confirmation."""

    conversation_id: str = Field(..., description="Conversation ID")
    confirmed: bool = Field(..., description="Whether user confirmed")


class ConfirmationResponse(BaseModel):
    """Response schema for transaction confirmation."""

    response: str = Field(..., description="Agent response message")
    transaction_id: str | None = Field(None, description="Transaction ID if executed")
    status: str = Field(..., description="Transaction status")