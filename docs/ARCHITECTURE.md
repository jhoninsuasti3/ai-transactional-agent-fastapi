# Documentación de Arquitectura

## Resumen

**AI Transactional Agent** es un sistema de IA conversacional construido con FastAPI y LangGraph que procesa transacciones financieras mediante lenguaje natural. El sistema implementa principios de Clean Architecture con patrones hexagonales para escalabilidad y mantenibilidad.

## Arquitectura del Sistema

### Componentes de Alto Nivel

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

### Diagrama de Componentes (Mermaid)

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

### Decisiones Clave de Diseño

**1. Integración del Agente**
- El agente LangGraph se ejecuta **en-proceso** dentro del orchestrator, no como servicio separado
- Importado directamente en `apps/orchestrator/v1/routers/chat.py`
- Simplifica el deployment y reduce latencia

**2. Servicios**
- ✅ **Orchestrator** (Docker) - Puerto 8002
- ✅ **Mock API** (Docker) - Puerto 8001
- ✅ **PostgreSQL** (Docker) - Puerto 5432

## Arquitectura en Capas

### Estructura del Proyecto

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

### Patrones Arquitectónicos

**1. Clean Architecture / Arquitectura Hexagonal**
- **Domain**: Lógica de negocio pura, independiente del framework
- **Application**: Casos de uso y servicios
- **Infrastructure**: Implementaciones técnicas (DB, HTTP, etc.)
- **API**: Capa de presentación (routers FastAPI)

**2. Patrón Repository**
Abstrae la capa de persistencia:

```python
from apps.orchestrator.domain.ports.repository_port import ConversationRepository

class ConversationRepositoryImpl(ConversationRepository):
    async def create(self, conversation: Conversation) -> Conversation:
        # Implementación con SQLAlchemy
        ...
```

**3. Inyección de Dependencias**
Dependencias de FastAPI para testing y modularidad:

```python
@router.post("/chat")
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    ...
```

## Arquitectura del Agente LangGraph

### Diagrama de Máquina de Estados del Agente

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
        Extrae teléfono y monto
        del lenguaje natural
    end note

    note right of validator_node
        Llama API externa
        para validar datos
    end note

    note right of transaction_node
        Ejecuta transacción
        vía API externa
    end note
```

### Máquina de Estados del Agente (Texto)

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

### Estado del Agente

```python
class ConversationState(MessagesState):
    """Estado del agente transaccional."""

    # Datos de la transacción
    phone: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "COP"

    # Validación
    validation_status: Optional[Literal["pending", "valid", "invalid"]] = None
    validation_error: Optional[str] = None

    # Confirmación
    confirmation: Optional[Literal["pending", "confirmed", "cancelled"]] = None

    # Resultado
    transaction_id: Optional[str] = None
    transaction_status: Optional[Literal["pending", "completed", "failed"]] = None

    # Metadatos
    conversation_id: str
    user_id: Optional[str] = None
```

### Nodos del Agente

**1. conversation_node** (apps/agents/transactional/nodes/conversation.py)
- Maneja la interacción con el usuario
- Genera respuestas conversacionales
- Guía el flujo de la conversación

**2. extractor_node** (apps/agents/transactional/nodes/extractor.py)
- Extrae número de teléfono y monto del contexto
- Usa salida estructurada del LLM
- Retorna: phone, amount

**3. validator_node** (apps/agents/transactional/nodes/validator.py)
- Valida la transacción con la API Mock
- POST /api/v1/transactions/validate
- Maneja errores de validación

**4. confirmation_node** (apps/agents/transactional/nodes/confirmation.py)
- Solicita confirmación del usuario
- Muestra resumen de la transacción
- Espera respuesta "sí/no"

**5. transaction_node** (apps/agents/transactional/nodes/transaction.py)
- Ejecuta la transacción
- POST /api/v1/transactions/execute
- Retorna el ID de transacción

### Rutas Condicionales

```python
def should_extract(state: ConversationState) -> str:
    """Ruta después de la conversación: extraer o finalizar."""
    # Si ya tenemos teléfono y monto, validar
    if state.get("phone") and state.get("amount"):
        return "validate"

    # Detectar palabras clave transaccionales
    messages = state.get("messages", [])
    transaction_keywords = ["envía", "enviar", "transferir", "$", "pesos", "número"]

    if last_user_msg and any(keyword in last_user_msg for keyword in transaction_keywords):
        return "extract"

    # Conversación simple → END
    return END
```

## Persistencia de Datos

### Estrategia de Base de Datos

**PostgreSQL** se utiliza para todos los datos persistentes:

**✅ Qué almacenar:**
- LangGraph Checkpoints - Estado del agente entre mensajes
- Datos de Dominio - tablas de conversations, transactions, messages
- Auditoría - Logs de transacciones

**Por qué PostgreSQL:**
- Cumple con ACID
- Consultas SQL complejas
- Bajo costo (disco vs RAM)
- Fácil debugging
- Escala a millones de conversaciones

### Esquema de Base de Datos

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

### Cadenas de Conexión

```python
# Para LangGraph (usa psycopg)
LANGGRAPH_CHECKPOINT_DB = "postgresql+psycopg://user:pass@host:5432/db"

# Para SQLAlchemy (usa asyncpg)
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"
```

## Endpoints de la API

### Orchestrator (puerto 8002)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificación de salud |
| GET | `/api/v1/` | Información de la API |
| POST | `/api/v1/chat` | Chat con el agente |
| GET | `/api/v1/conversations/{id}` | Obtener conversación |
| GET | `/api/v1/transactions/{id}` | Obtener transacción |

**Esquema de Petición Chat:**
```json
{
  "message": "Envía $50000 al 3001234567",
  "user_id": "user-001",
  "conversation_id": "conv-123"  // Optional
}
```

**Esquema de Respuesta Chat:**
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

### Mock API (puerto 8001)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificación de salud |
| POST | `/api/v1/transactions/validate` | Validar transacción |
| POST | `/api/v1/transactions/execute` | Ejecutar transacción |
| GET | `/api/v1/transactions/{id}` | Obtener estado de transacción |

## Flujos Completos

### Flujo 1: Conversación Simple (Sin Transacción)

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

### Flujo 2: Transacción Exitosa

#### Diagrama de Secuencia (Mermaid)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant API as FastAPI
    participant Agent as Agente LangGraph
    participant DB as PostgreSQL
    participant Mock as API Mock

    U->>+API: POST /api/v1/chat<br/>"Envía $75000 al 3109876543"
    API->>+Agent: invoke(state)

    Note over Agent: conversation_node
    Agent->>Agent: Generar respuesta

    Note over Agent: should_extract() = True
    Note over Agent: extractor_node
    Agent->>Agent: Extraer phone=3109876543<br/>amount=75000

    Note over Agent: should_validate() = True
    Note over Agent: validator_node
    Agent->>+Mock: POST /validate
    Mock-->>-Agent: {"is_valid": true, "validation_id": "VAL-xyz"}

    Note over Agent: should_confirm() = True
    Note over Agent: confirmation_node
    Agent->>Agent: Configurar needs_confirmation=true
    Agent-->>-API: "Confirmas envío de $75,000..."
    API-->>-U: Respuesta con solicitud de confirmación

    U->>+API: POST /api/v1/chat<br/>"Sí, confirmo"
    API->>+Agent: invoke(state)

    Note over Agent: confirmation_node
    Agent->>Agent: Detectar confirmación

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

#### Flujo de Texto

```
1. Usuario: "Envía $75000 al 3109876543"
   ↓
2. POST /api/v1/chat
   ↓
3. LangGraph:
   conversation_node → genera respuesta inicial
   ↓
   should_extract() → detecta palabras clave: "Envía", "$", número
   ↓
   extractor_node → extrae phone=3109876543, amount=75000
   ↓
   should_validate() → tiene phone y amount
   ↓
   validator_node → llama a Mock API POST /validate
   ↓
4. Mock API:
   Valida: teléfono 10 dígitos ✓
          monto > 1000 y < 5000000 ✓
   ↓
   Retorna: {"is_valid": true, "validation_id": "VAL-xyz"}
   ↓
5. LangGraph:
   should_confirm() → state["needs_confirmation"] = true
   ↓
   confirmation_node → solicita confirmación
   ↓
6. Usuario: "Sí, confirmo"
   ↓
7. LangGraph:
   should_execute() → state["confirmed"] = true
   ↓
   transaction_node → llama a Mock API POST /execute
   ↓
8. Mock API:
   Ejecuta transacción (70% éxito, 20% pendiente, 10% fallo)
   ↓
   Retorna: {"transaction_id": "TXN-123", "status": "completed"}
   ↓
9. conversation_node → genera mensaje de confirmación
   ↓
10. Guarda en PostgreSQL:
    - LangGraph checkpoint
    - Registro de transacción
   ↓
11. Respuesta:
    {
      "response": "Tu transferencia de $75,000 ha sido completada...",
      "transaction_id": "TXN-123",
      "metadata": {"status": "completed", ...}
    }
```

## Soporte Multi-LLM

### Configuración

El sistema soporta múltiples proveedores LLM mediante variable de entorno:

```python
# .env
LLM_PROVIDER=openai  # o anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Beneficios:**
- ✅ Flexibilidad para cambiar proveedores sin cambios de código
- ✅ Usar modelos específicos (GPT-4o-mini vs Claude 3.5 Sonnet)
- ✅ Mitigación de riesgo si un proveedor falla
- ✅ Optimización de costos basada en caso de uso

## Patrones de Resiliencia

### Cliente HTTP con Resiliencia

El sistema implementa:
- **Retry con backoff exponencial**: 3 intentos con delays de 1s, 2s, 4s
- **Circuit breaker**: Se abre tras 5 fallos, se resetea tras 60s
- **Timeouts**: Timeout de conexión 5s, timeout de lectura 10s

### Estados del Circuit Breaker

```
CLOSED → (5 fallos) → OPEN
  ↑                       ↓
  └─ (éxito) ← HALF_OPEN ← (60s timeout)
```

## Configuración

### Configuraciones Críticas

En `apps/orchestrator/core/config.py`:

```python
class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "AI Transactional Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production", "testing"]

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8002

    # Base de datos
    DATABASE_URL: str  # postgresql+asyncpg://...
    LANGGRAPH_CHECKPOINT_DB: str  # postgresql+psycopg://...

    # OpenAI
    OPENAI_API_KEY: str  # Requerido
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7

    # Servicio de Transacciones
    TRANSACTION_SERVICE_URL: str = "http://localhost:8001"

    # Resiliencia
    MAX_RETRIES: int = 3
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60
```

### Variables de Entorno

```bash
# Aplicación
ENVIRONMENT=development
DEBUG=true

# Base de datos (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/transactional_agent
LANGGRAPH_CHECKPOINT_DB=postgresql+psycopg://postgres:postgres@postgres:5432/transactional_agent

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Servicios
TRANSACTION_SERVICE_URL=http://mock-api:8001
```

## Estrategia de Testing

```
tests/
├── unit/               # Tests unitarios
│   ├── agents/         # Tests de agentes
│   └── orchestrator/   # Tests de orchestrator
├── integration/        # Tests de integración
│   ├── test_chat_integration.py
│   └── test_transaction_flows.py
└── conftest.py        # Fixtures de Pytest
```

**Cobertura Actual: 80%**

## Deployment

### Docker Compose

```bash
# Construir e iniciar servicios
docker compose up -d --build

# Verificar salud
make health

# Ver logs
docker compose logs -f orchestrator
```

### Health Checks

```bash
# Mock API
curl http://localhost:8001/health

# Orchestrator
curl http://localhost:8002/health
```

## Stack de Middleware

El orden es importante:

1. **RequestIDMiddleware**: Asigna ID único a cada petición
2. **LoggingMiddleware**: Registra peticiones/respuestas
3. **CORSMiddleware**: Maneja CORS
4. **Exception Handlers**: Manejo centralizado de errores

## Manejo de Excepciones

Sistema de manejo de excepciones centralizado:

```python
from apps.orchestrator.domain.exceptions.base import EntityNotFoundError

# En el código
raise EntityNotFoundError("Conversation", conversation_id)

# Automáticamente se convierte a:
# {
#   "error": "Conversation with id '123' not found",
#   "details": {"entity_name": "Conversation", "entity_id": 123},
#   "timestamp": "2025-01-22T..."
# }
```

## Optimización de Costos LLM

### Estrategias para Reducir Costos

**1. Usar Modelos Mini/Nano**
```python
OPENAI_MODEL = "gpt-4o-mini"  # ~10x menos tokens que GPT-4
```

**2. Limitar Historial**
```python
MAX_HISTORY_MESSAGES = 10  # Solo los últimos 10 mensajes
messages_to_send = messages[-MAX_HISTORY_MESSAGES:]
```

**3. System Prompts Concisos**
```python
# Bueno (conciso)
"""Asistente de transferencias. Solicita: teléfono (10 dígitos), monto.
Pide confirmación antes de ejecutar."""

# Malo (verboso)
"""You are a helpful assistant that helps users transfer money.
You should be polite, professional, and always ask for confirmation..."""
```

**4. Truncado de Contexto**
```python
MAX_TOKENS_PER_MESSAGE = 500
truncated_content = message.content[:MAX_TOKENS_PER_MESSAGE]
```

## Correcciones Críticas Aplicadas

### 1. Corrección de Recursión Infinita

**Problema:**
```
conversation → should_extract → extract
      ↑                            ↓
      └──────── conversation ←──────┘
               (BUCLE INFINITO)
```

**Solución:**
Se agregó enrutamiento condicional a END para conversaciones simples:

```python
def should_extract(state: ConversationState) -> str:
    """Ruta después de la conversación: extraer o finalizar."""
    # ... lógica de detección
    return END  # Para conversaciones simples
```

### 2. Configuración de LangGraph Checkpoint

Se agregó `LANGGRAPH_CHECKPOINT_DB` con formato correcto:

```python
# LangGraph usa psycopg (no asyncpg)
LANGGRAPH_CHECKPOINT_DB = "postgresql+psycopg://user:pass@host:5432/db"
```

## Referencias

- **README del Proyecto**: `/README.md`
- **Configuración Docker**: `docs/DOCKER.md`
- **Guía de Testing**: `docs/TESTING.md`
- **Guía de Desarrollo**: `docs/DEVELOPMENT.md`
- **Documentación LangGraph**: https://langchain-ai.github.io/langgraph/
- **Documentación FastAPI**: https://fastapi.tiangolo.com/
