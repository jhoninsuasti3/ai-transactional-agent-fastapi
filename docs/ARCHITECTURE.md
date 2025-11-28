# Architecture Documentation

## Overview

**AI Transactional Agent** is a conversational AI system built with FastAPI and LangGraph that processes financial transactions through natural language conversations. The system implements Clean Architecture principles with hexagonal patterns for scalability and maintainability.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE / USUARIO                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP POST /api/v1/chat
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         ORCHESTRATOR (Puerto 8002) - CONTENEDOR ÚNICO        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                        │ │
│  │  Endpoints: /health, /api/v1/chat, /api/v1/            │ │
│  └──────────────────┬─────────────────────────────────────┘ │
│                     │                                        │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         LangGraph Agent (Integrated in Process)        │ │
│  │                                                         │ │
│  │  conversation → should_extract → [extract | END]      │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │          extractor → should_validate           │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │         [validate | conversation]              │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │          validator → should_confirm            │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │      [confirmation | END]                      │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │        confirmation → should_execute           │ │
│  │       │              │                                  │ │
│  │       │              ▼                                  │ │
│  │       │       [transaction | END]                      │ │
│  │       │              │                                  │ │
│  │       └──────────────┘                                  │ │
│  │                                                         │ │
│  └──────────────────┬──────────────────┬─────────────────┘ │
└───────────────────┬─┴──────────────────┴───────────────────┘
                    │                    │
                    ▼                    ▼
        ┌──────────────────┐  ┌───────────────────────┐
        │   PostgreSQL     │  │  Mock Transaction API │
        │   (Puerto 5432)  │  │  (Puerto 8001)        │
        │                  │  │                       │
        │ • Checkpoints    │  │  POST /api/v1/        │
        │   (LangGraph)    │  │    transactions/      │
        │ • Domain Data:   │  │    validate           │
        │   - conversations│  │  POST /api/v1/        │
        │   - transactions │  │    transactions/      │
        │   - messages     │  │    execute            │
        └──────────────────┘  │  GET  /api/v1/        │
                              │    transactions/{id}  │
                              └───────────────────────┘
```

### Component Diagram (Mermaid)

```mermaid
graph TB
    User[Cliente/Usuario]

    subgraph Orchestrator["Orchestrator Container (Port 8002)"]
        API[FastAPI Application<br/>/api/v1/chat]

        subgraph Agent["LangGraph Agent (In-Process)"]
            Conv[conversation_node]
            Extr[extractor_node]
            Valid[validator_node]
            Conf[confirmation_node]
            Trans[transaction_node]

            Conv -->|should_extract?| Extr
            Conv -->|no extract| EndConv[END]
            Extr -->|should_validate?| Valid
            Extr -->|missing data| Conv
            Valid -->|should_confirm?| Conf
            Valid -->|invalid| Conv
            Conf -->|should_execute?| Trans
            Conf -->|cancel| EndCancel[END]
            Trans --> EndTrans[END]
        end

        Persist[Persistence Service]
        Client[Transaction Client]
    end

    DB[(PostgreSQL<br/>Port 5432)]
    MockAPI[Mock Transaction API<br/>Port 8001]

    User -->|POST /api/v1/chat| API
    API --> Agent
    Agent --> Persist
    Agent --> Client
    Persist -->|Store| DB
    Client -->|HTTP| MockAPI

    style Orchestrator fill:#e1f5ff
    style Agent fill:#fff3cd
    style DB fill:#d4edda
    style MockAPI fill:#d4edda
```

### Key Design Decisions

**1. Agent Integration**
- The LangGraph agent runs **in-process** within the orchestrator, not as a separate service
- Imported directly in `apps/orchestrator/v1/routers/chat.py:apps/orchestrator/v1/routers/chat.py`
- Simplifies deployment and reduces latency

**2. Services**
- ✅ **Orchestrator** (Docker) - Port 8002
- ✅ **Mock API** (Docker) - Port 8001
- ✅ **PostgreSQL** (Docker) - Port 5432

## Layered Architecture

### Project Structure

```
apps/
├── agents/                 # AI Agents Module (LangGraph)
│   └── transactional/      # Transactional agent
│       ├── agent.py        # Graph factory
│       ├── config.py       # Multi-LLM configuration
│       ├── state.py        # State definition
│       ├── nodes/          # Agent nodes
│       ├── routes/         # Conditional routes
│       ├── tools/          # LangChain tools
│       └── prompts/        # LLM prompts
│
├── orchestrator/           # FastAPI Application
│   ├── api/                # API Layer
│   │   ├── app.py          # Application factory
│   │   ├── health/         # Health checks
│   │   ├── middlewares/    # HTTP middlewares
│   │   └── exception_handlers/
│   ├── v1/                 # API Version 1
│   │   ├── routers/        # Endpoint routers
│   │   └── schemas/        # Pydantic schemas
│   ├── services/           # Application services
│   ├── domain/             # Domain Layer
│   │   ├── entities/       # Domain entities
│   │   ├── models.py       # Domain models
│   │   └── ports/          # Interfaces (Hexagonal)
│   ├── infrastructure/     # Infrastructure Layer
│   │   ├── clients/        # HTTP clients
│   │   └── persistence/    # ORM/Database
│   └── core/               # Core utilities
│       ├── config.py       # Settings
│       ├── exceptions.py   # Custom exceptions
│       └── logging.py      # Logging configuration
```

### Architectural Patterns

**1. Clean Architecture / Hexagonal Architecture**
- **Domain**: Pure business logic, framework-independent
- **Application**: Use cases and services
- **Infrastructure**: Technical implementations (DB, HTTP, etc.)
- **API**: Presentation layer (FastAPI routers)

**2. Repository Pattern**
Abstracts persistence layer:

```python
from apps.orchestrator.domain.ports.repository_port import ConversationRepository

class ConversationRepositoryImpl(ConversationRepository):
    async def create(self, conversation: Conversation) -> Conversation:
        # SQLAlchemy implementation
        ...
```

**3. Dependency Injection**
FastAPI dependencies for testing and modularity:

```python
@router.post("/chat")
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    ...
```

## LangGraph Agent Architecture

### Agent State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> conversation_node

    conversation_node --> should_extract
    should_extract --> extractor_node: needs_extraction
    should_extract --> [*]: simple_conversation

    extractor_node --> should_validate
    should_validate --> validator_node: has_data
    should_validate --> conversation_node: missing_data

    validator_node --> should_confirm
    should_confirm --> confirmation_node: valid
    should_confirm --> conversation_node: invalid

    confirmation_node --> should_execute
    should_execute --> transaction_node: confirmed
    should_execute --> [*]: cancelled

    transaction_node --> conversation_node: success/failure
    conversation_node --> [*]: end_conversation

    note right of extractor_node
        Extract phone + amount
        from natural language
    end note

    note right of validator_node
        Call external API
        to validate data
    end note

    note right of transaction_node
        Execute transaction
        via external API
    end note
```

### Agent State Machine (Text)

```
START → conversation → should_extract
                         ├→ extract (if needs extraction)
                         └→ END (if simple conversation)
                              ↓
                         extractor → should_validate
                                       ├→ validate
                                       └→ conversation
                                            ↓
                         validator → should_confirm
                                       ├→ confirmation
                                       └→ END
                                            ↓
                         confirmation → should_execute
                                          ├→ transaction
                                          └→ END (if cancelled)
                                               ↓
                         transaction → conversation → END
```

### Agent State

```python
class ConversationState(MessagesState):
    """State for the transactional agent."""

    # Transaction data
    phone: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "COP"

    # Validation
    validation_status: Optional[Literal["pending", "valid", "invalid"]] = None
    validation_error: Optional[str] = None

    # Confirmation
    confirmation: Optional[Literal["pending", "confirmed", "cancelled"]] = None

    # Result
    transaction_id: Optional[str] = None
    transaction_status: Optional[Literal["pending", "completed", "failed"]] = None

    # Metadata
    conversation_id: str
    user_id: Optional[str] = None
```

### Agent Nodes

**1. conversation_node** (apps/agents/transactional/nodes/conversation.py)
- Handles user interaction
- Generates conversational responses
- Guides the conversation flow

**2. extractor_node** (apps/agents/transactional/nodes/extractor.py)
- Extracts phone number and amount from context
- Uses LLM structured output
- Returns: phone, amount

**3. validator_node** (apps/agents/transactional/nodes/validator.py)
- Validates transaction with Mock API
- POST /api/v1/transactions/validate
- Handles validation errors

**4. confirmation_node** (apps/agents/transactional/nodes/confirmation.py)
- Requests user confirmation
- Shows transaction summary
- Waits for "yes/no" response

**5. transaction_node** (apps/agents/transactional/nodes/transaction.py)
- Executes transaction
- POST /api/v1/transactions/execute
- Returns transaction ID

### Conditional Routes

```python
def should_extract(state: ConversationState) -> str:
    """Route after conversation: extract or end."""
    # If already have phone and amount, validate
    if state.get("phone") and state.get("amount"):
        return "validate"

    # Detect transactional keywords
    messages = state.get("messages", [])
    transaction_keywords = ["envía", "enviar", "transferir", "$", "pesos", "número"]

    if last_user_msg and any(keyword in last_user_msg for keyword in transaction_keywords):
        return "extract"

    # Simple conversation → END
    return END
```

## Data Persistence

### Database Strategy

**PostgreSQL** is used for all persistent data:

**✅ What to store:**
- LangGraph Checkpoints - Agent state between messages
- Domain Data - conversations, transactions, messages tables
- Audit - Transaction logs

**Why PostgreSQL:**
- ACID compliant
- Complex SQL queries
- Low cost (disk vs RAM)
- Easy debugging
- Scales to millions of conversations

### Database Schema

```sql
-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    transaction_id VARCHAR(255) UNIQUE,
    recipient_phone VARCHAR(15) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'COP',
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(50),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LangGraph uses its own "checkpoints" table
-- (created automatically by PostgresSaver)
```

### Connection Strings

```python
# For LangGraph (uses psycopg)
LANGGRAPH_CHECKPOINT_DB = "postgresql+psycopg://user:pass@host:5432/db"

# For SQLAlchemy (uses asyncpg)
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"
```

## API Endpoints

### Orchestrator (port 8002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/` | API info |
| POST | `/api/v1/chat` | Chat with agent |
| GET | `/api/v1/conversations/{id}` | Get conversation |
| GET | `/api/v1/transactions/{id}` | Get transaction |

**Chat Request Schema:**
```json
{
  "message": "Envía $50000 al 3001234567",
  "user_id": "user-001",
  "conversation_id": "conv-123"  // Optional
}
```

**Chat Response Schema:**
```json
{
  "response": "He procesado tu transferencia...",
  "conversation_id": "conv-abc123",
  "transaction_id": "TXN-xyz789",
  "requires_confirmation": false,
  "metadata": {
    "phone": "3001234567",
    "amount": 50000,
    "status": "completed"
  }
}
```

### Mock API (port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/transactions/validate` | Validate transaction |
| POST | `/api/v1/transactions/execute` | Execute transaction |
| GET | `/api/v1/transactions/{id}` | Get transaction status |

## Complete Flows

### Flow 1: Simple Conversation (No Transaction)

```
1. User: "Hola, ¿cómo estás?"
   ↓
2. POST /api/v1/chat
   {
     "message": "Hola, ¿cómo estás?",
     "user_id": "user-001"
   }
   ↓
3. Orchestrator → agent.invoke()
   ↓
4. LangGraph:
   conversation_node → generates conversational response
   ↓
   should_extract() → detects NO transactional keywords
   ↓
   RETURNS END (no loop)
   ↓
5. Saves checkpoint in PostgreSQL
   ↓
6. Response:
   {
     "response": "¡Hola! Estoy aquí para ayudarte...",
     "conversation_id": "conv-abc123",
     "transaction_id": null
   }
```

### Flow 2: Successful Transaction

#### Sequence Diagram (Mermaid)

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant Agent as LangGraph Agent
    participant DB as PostgreSQL
    participant Mock as Mock API

    U->>+API: POST /api/v1/chat<br/>"Envía $75000 al 3109876543"
    API->>+Agent: invoke(state)

    Note over Agent: conversation_node
    Agent->>Agent: Generate response

    Note over Agent: should_extract() = True
    Note over Agent: extractor_node
    Agent->>Agent: Extract phone=3109876543<br/>amount=75000

    Note over Agent: should_validate() = True
    Note over Agent: validator_node
    Agent->>+Mock: POST /validate
    Mock-->>-Agent: {"is_valid": true, "validation_id": "VAL-xyz"}

    Note over Agent: should_confirm() = True
    Note over Agent: confirmation_node
    Agent->>Agent: Set needs_confirmation=true
    Agent-->>-API: "Confirmas envío de $75,000..."
    API-->>-U: Response with confirmation request

    U->>+API: POST /api/v1/chat<br/>"Sí, confirmo"
    API->>+Agent: invoke(state)

    Note over Agent: confirmation_node
    Agent->>Agent: Detect confirmation

    Note over Agent: should_execute() = True
    Note over Agent: transaction_node
    Agent->>+Mock: POST /execute
    Mock-->>-Agent: {"transaction_id": "TXN-123", "status": "completed"}

    Agent->>+DB: Save transaction
    DB-->>-Agent: Stored
    Agent->>+DB: Save checkpoint
    DB-->>-Agent: Stored

    Note over Agent: conversation_node
    Agent->>Agent: Generate success message
    Agent-->>-API: Success with TXN-123
    API-->>-U: "Transacción completada"
```

#### Text Flow

```
1. User: "Envía $75000 al 3109876543"
   ↓
2. POST /api/v1/chat
   ↓
3. LangGraph:
   conversation_node → generates initial response
   ↓
   should_extract() → detects keywords: "Envía", "$", number
   ↓
   extractor_node → extracts phone=3109876543, amount=75000
   ↓
   should_validate() → has phone and amount
   ↓
   validator_node → calls Mock API POST /validate
   ↓
4. Mock API:
   Validates: phone 10 digits ✓
             amount > 1000 and < 5000000 ✓
   ↓
   Returns: {"is_valid": true, "validation_id": "VAL-xyz"}
   ↓
5. LangGraph:
   should_confirm() → state["needs_confirmation"] = true
   ↓
   confirmation_node → requests confirmation
   ↓
6. User: "Sí, confirmo"
   ↓
7. LangGraph:
   should_execute() → state["confirmed"] = true
   ↓
   transaction_node → calls Mock API POST /execute
   ↓
8. Mock API:
   Executes transaction (70% success, 20% pending, 10% failed)
   ↓
   Returns: {"transaction_id": "TXN-123", "status": "completed"}
   ↓
9. conversation_node → generates confirmation message
   ↓
10. Saves in PostgreSQL:
    - LangGraph checkpoint
    - Transaction record
   ↓
11. Response:
    {
      "response": "Tu transferencia de $75,000 ha sido completada...",
      "transaction_id": "TXN-123",
      "metadata": {"status": "completed", ...}
    }
```

## Multi-LLM Support

### Configuration

The system supports multiple LLM providers via environment variable:

```python
# .env
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Benefits:**
- ✅ Flexibility to switch providers without code changes
- ✅ Use specific models (GPT-4o-mini vs Claude 3.5 Sonnet)
- ✅ Risk mitigation if one provider fails
- ✅ Cost optimization based on use case

## Resilience Patterns

### HTTP Client with Resilience

The system implements:
- **Retry with exponential backoff**: 3 attempts with 1s, 2s, 4s delays
- **Circuit breaker**: Opens after 5 failures, resets after 60s
- **Timeouts**: Connection timeout 5s, read timeout 10s

### Circuit Breaker States

```
CLOSED → (5 failures) → OPEN
  ↑                       ↓
  └─ (success) ← HALF_OPEN ← (60s timeout)
```

## Configuration

### Critical Settings

In `apps/orchestrator/core/config.py`:

```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Transactional Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production", "testing"]

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8002

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://...
    LANGGRAPH_CHECKPOINT_DB: str  # postgresql+psycopg://...

    # OpenAI
    OPENAI_API_KEY: str  # Required
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7

    # Transaction Service
    TRANSACTION_SERVICE_URL: str = "http://localhost:8001"

    # Resilience
    MAX_RETRIES: int = 3
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60
```

### Environment Variables

```bash
# Application
ENVIRONMENT=development
DEBUG=true

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/transactional_agent
LANGGRAPH_CHECKPOINT_DB=postgresql+psycopg://postgres:postgres@postgres:5432/transactional_agent

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Services
TRANSACTION_SERVICE_URL=http://mock-api:8001
```

## Testing Strategy

```
tests/
├── unit/               # Unit tests
│   ├── agents/         # Agent tests
│   └── orchestrator/   # Orchestrator tests
├── integration/        # Integration tests
│   ├── test_chat_integration.py
│   └── test_transaction_flows.py
└── conftest.py        # Pytest fixtures
```

**Current Coverage: 74%**

## Deployment

### Docker Compose

```bash
# Build and start services
docker compose up -d --build

# Check health
make health

# View logs
docker compose logs -f orchestrator
```

### Health Checks

```bash
# Mock API
curl http://localhost:8001/health

# Orchestrator
curl http://localhost:8002/health
```

## Middleware Stack

Order is important:

1. **RequestIDMiddleware**: Assigns unique ID to each request
2. **LoggingMiddleware**: Logs requests/responses
3. **CORSMiddleware**: Handles CORS
4. **Exception Handlers**: Centralized error handling

## Exception Handling

Centralized exception handling system:

```python
from apps.orchestrator.domain.exceptions.base import EntityNotFoundError

# In code
raise EntityNotFoundError("Conversation", conversation_id)

# Automatically converts to:
# {
#   "error": "Conversation with id '123' not found",
#   "details": {"entity_name": "Conversation", "entity_id": 123},
#   "timestamp": "2025-01-22T..."
# }
```

## LLM Cost Optimization

### Strategies to Reduce Costs

**1. Use Mini/Nano Models**
```python
OPENAI_MODEL = "gpt-4o-mini"  # ~10x less tokens than GPT-4
```

**2. Limit History**
```python
MAX_HISTORY_MESSAGES = 10  # Only last 10 messages
messages_to_send = messages[-MAX_HISTORY_MESSAGES:]
```

**3. Concise System Prompts**
```python
# Good (concise)
"""Asistente de transferencias. Solicita: teléfono (10 dígitos), monto.
Pide confirmación antes de ejecutar."""

# Bad (verbose)
"""You are a helpful assistant that helps users transfer money.
You should be polite, professional, and always ask for confirmation..."""
```

**4. Context Truncation**
```python
MAX_TOKENS_PER_MESSAGE = 500
truncated_content = message.content[:MAX_TOKENS_PER_MESSAGE]
```

## Critical Fixes Applied

### 1. Infinite Recursion Fix

**Problem:**
```
conversation → should_extract → extract
      ↑                            ↓
      └──────── conversation ←──────┘
               (INFINITE LOOP)
```

**Solution:**
Added conditional routing to END for simple conversations:

```python
def should_extract(state: ConversationState) -> str:
    """Route after conversation: extract or end."""
    # ... detection logic
    return END  # For simple conversations
```

### 2. LangGraph Checkpoint Configuration

Added `LANGGRAPH_CHECKPOINT_DB` with correct format:

```python
# LangGraph uses psycopg (not asyncpg)
LANGGRAPH_CHECKPOINT_DB = "postgresql+psycopg://user:pass@host:5432/db"
```

## References

- **Project README**: `/README.md`
- **Docker Setup**: `docs/DOCKER.md`
- **Testing Guide**: `docs/TESTING.md`
- **Development Guide**: `docs/DEVELOPMENT.md`
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
