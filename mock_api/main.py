"""
Mock Transaction API - Simulates external payment service.

This is a simple mock API service that simulates an external transaction
processing system. It implements realistic behaviors like latency, random
failures, and state transitions.

Run with: uvicorn mock_api.main:app --reload --port 8001
"""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mock_api.routers import transactions

# Create FastAPI app
app = FastAPI(
    title="Mock Transaction API",
    description="Mock API for simulating external transaction processing service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mock-transaction-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Mock Transaction API",
        "version": "1.0.0",
        "description": "Simulates external transaction processing service",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "validate": "POST /api/v1/transactions/validate",
            "execute": "POST /api/v1/transactions/execute",
            "status": "GET /api/v1/transactions/{transaction_id}",
        },
        "features": [
            "Realistic latency simulation (100-500ms)",
            "Random failures (10% probability)",
            "State transitions: pending -> completed/failed",
            "Validation before execution",
        ],
    }
