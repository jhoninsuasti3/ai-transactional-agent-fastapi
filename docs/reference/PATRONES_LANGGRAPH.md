# Patrones LangGraph Enterprise - Referencia Moderna

> Guía de implementación de LangGraph 0.2.x para agentes conversacionales transaccionales en producción.
> Basado en best practices enterprise y documentación oficial.

**Última actualización**: 2025-01-21
**Versión LangGraph**: 0.2.27+
**Versión LangChain**: 0.3.0+

---

## 📋 Índice

1. [Diferencias Clave: LangChain vs LangGraph](#diferencias-clave)
2. [Arquitectura Recomendada](#arquitectura-recomendada)
3. [State Management](#state-management)
4. [Nodos del Grafo](#nodos-del-grafo)
5. [Patrones de Routing](#patrones-de-routing)
6. [Persistencia con PostgreSQL](#persistencia-con-postgresql)
7. [Integración con FastAPI](#integración-con-fastapi)
8. [Testing Patterns](#testing-patterns)
9. [Observabilidad](#observabilidad)
10. [Patrones Avanzados](#patrones-avanzados)

---

## 1. Diferencias Clave: LangChain vs LangGraph {#diferencias-clave}

### LangChain (Chains Simples)

```python
# ❌ Antiguo: LangChain 0.0.x
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=ConversationBufferMemory()
)

# Flujo lineal, sin control fino
response = chain.run(input="Hello")
```

**Limitaciones**:
- Flujo secuencial solamente
- Sin control de estado estructurado
- Memoria limitada (buffer simple)
- No hay checkpointing
- Difícil debugging

---

### LangGraph (State Machines)

```python
# ✅ Moderno: LangGraph 0.2.x
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver

class AgentState(TypedDict):
    messages: list[BaseMessage]
    stage: str
    data: dict

workflow = StateGraph(AgentState)
workflow.add_node("extract", extract_node)
workflow.add_node("validate", validate_node)
workflow.add_conditional_edges("extract", route_fn)

graph = workflow.compile(
    checkpointer=PostgresSaver(...)
)

# Control total, checkpointing automático
result = await graph.ainvoke(initial_state, config)
```

**Ventajas**:
- State machines explícitos
- Conditional routing
- Checkpointing nativo (PostgreSQL, SQLite)
- Time-travel debugging
- Perfect para flujos transaccionales

---

## 2. Arquitectura Recomendada {#arquitectura-recomendada}

### Estructura de Carpetas

```
`apps/
├── application/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py              # AgentState definition
│   │   ├── graph.py              # StateGraph compilation
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── extract_info.py
│   │   │   ├── validate.py
│   │   │   ├── confirm.py
│   │   │   └── execute.py
│   │   ├── edges/
│   │   │   ├── __init__.py
│   │   │   └── routing.py       # Conditional edge logic
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── validate_transaction.py
│   │       └── execute_transaction.py
│   └── use_cases/
│       └── process_message.py
├── infrastructure/
│   ├── checkpointer/
│   │   ├── __init__.py
│   │   └── postgres_checkpointer.py
│   └── clients/
│       └── transaction_api.py
└── api/
    ├── routes/
    │   └── chat.py
    └── schemas/
        └── chat.py
```

---

## 3. State Management {#state-management}

### State Definition (TypedDict con Annotations)

```python
# apps/application/agent/state.py

from typing import Annotated, TypedDict, Literal
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Estado compartido del agente conversacional.

    IMPORTANTE:
    - Use Annotated para reducers personalizados
    - add_messages es el reducer por defecto para mensajes
    - Todos los campos deben tener valores por defecto o ser Optional
    """

    # Mensajes - se agregan con add_messages reducer
    messages: Annotated[list[AnyMessage], add_messages]

    # Datos extraídos
    recipient_phone: str | None
    amount: float | None

    # Control de flujo - CRÍTICO para conditional edges
    stage: Literal[
        "greeting",
        "extracting_phone",
        "extracting_amount",
        "validating",
        "confirming",
        "executing",
        "completed",
        "error"
    ]

    # Estado de validación
    validation_result: dict | None
    execution_result: dict | None

    # Confirmación del usuario
    awaiting_confirmation: bool
    user_confirmed: bool | None

    # Metadata
    conversation_id: str
    user_id: str
    transaction_id: str | None
    error_message: str | None
```

### Reducer Personalizado (Opcional)

```python
from operator import add

def aggregate_data(existing: dict, new: dict) -> dict:
    """Reducer personalizado para agregar datos sin sobrescribir"""
    return {**existing, **new}

class AgentState(TypedDict):
    # Con reducer personalizado
    metadata: Annotated[dict, aggregate_data]
```

---

## 4. Nodos del Grafo {#nodos-del-grafo}

### Patrón General de Nodo

```python
# Cada nodo recibe state y retorna dict parcial con updates

async def node_function(state: AgentState) -> dict:
    """
    Nodo del grafo.

    Args:
        state: Estado actual completo

    Returns:
        dict: Updates parciales al estado (no el estado completo)
    """
    # 1. Leer del estado
    current_stage = state["stage"]
    messages = state["messages"]

    # 2. Ejecutar lógica
    result = await some_operation(messages)

    # 3. Retornar SOLO los cambios
    return {
        "stage": "next_stage",
        "some_field": result,
        "messages": [AIMessage(content="Response")]
    }
```

### Nodo de Extracción de Información

```python
# apps/application/agent/nodes/extract_info.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

class ExtractedInfo(BaseModel):
    """Schema para function calling"""
    recipient_phone: str | None = Field(
        None,
        description="Número de teléfono de 10 dígitos, comenzando con 3"
    )
    amount: float | None = Field(
        None,
        description="Monto a enviar, debe ser mayor a 0"
    )

async def extract_information_node(state: AgentState) -> dict:
    """
    Extrae información usando function calling de OpenAI.

    Pattern: Use structured output en lugar de parsing manual.
    """
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # Bind function para structured output
    llm_with_tools = llm.with_structured_output(ExtractedInfo)

    system_prompt = """Extrae información de transacción del usuario.

Si falta información, retorna None en ese campo.
NO inventes datos.
"""

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]

    extracted = await llm_with_tools.ainvoke(messages)

    # Determinar siguiente stage
    has_phone = extracted.recipient_phone is not None
    has_amount = extracted.amount is not None

    if has_phone and has_amount:
        next_stage = "validating"
    elif has_phone:
        next_stage = "extracting_amount"
    else:
        next_stage = "extracting_phone"

    return {
        "recipient_phone": extracted.recipient_phone,
        "amount": extracted.amount,
        "stage": next_stage,
    }
```

### Nodo de Validación

```python
# apps/application/agent/nodes/validate.py

from src.infrastructure.clients.transaction_api import ResilientTransactionAPIClient

async def validate_transaction_node(state: AgentState) -> dict:
    """
    Valida transacción con API externa usando patrones de resiliencia.
    """
    client = ResilientTransactionAPIClient(base_url="http://mock-api:8001")

    try:
        result = await client.validate_transaction(
            phone=state["recipient_phone"],
            amount=state["amount"]
        )

        if result["is_valid"]:
            return {
                "stage": "confirming",
                "validation_result": result,
            }
        else:
            return {
                "stage": "error",
                "error_message": result.get("error", "Validation failed"),
                "validation_result": result,
            }

    except Exception as e:
        return {
            "stage": "error",
            "error_message": f"Service error: {str(e)}",
        }
```

### Nodo de Confirmación

```python
# apps/application/agent/nodes/confirm.py

async def confirm_transaction_node(state: AgentState) -> dict:
    """
    Genera mensaje de confirmación y marca que esperamos respuesta.
    """
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    confirmation_prompt = f"""Genera un mensaje de confirmación profesional.

Datos:
- Teléfono: {state['recipient_phone']}
- Monto: ${state['amount']:,.0f} COP

Pide confirmación explícita ('Sí, confirmo' o 'No').
Máximo 2-3 oraciones."""

    response = await llm.ainvoke([SystemMessage(content=confirmation_prompt)])

    return {
        "awaiting_confirmation": True,
        "messages": [AIMessage(content=response.content)],
    }
```

### Nodo de Ejecución

```python
# apps/application/agent/nodes/execute.py

async def execute_transaction_node(state: AgentState) -> dict:
    """
    Ejecuta transacción confirmada.
    """
    client = ResilientTransactionAPIClient(base_url="http://mock-api:8001")

    try:
        result = await client.execute_transaction(
            phone=state["recipient_phone"],
            amount=state["amount"]
        )

        return {
            "stage": "completed",
            "transaction_id": result["transaction_id"],
            "execution_result": result,
            "messages": [
                AIMessage(
                    content=f"Transacción completada. ID: {result['transaction_id']}"
                )
            ],
        }

    except Exception as e:
        return {
            "stage": "error",
            "error_message": f"Execution failed: {str(e)}",
        }
```

---

## 5. Patrones de Routing {#patrones-de-routing}

### Conditional Edges

```python
# apps/application/agent/edges/routing.py

from typing import Literal

def route_after_extraction(
    state: AgentState
) -> Literal["validate", "continue_extracting", "generate_response"]:
    """
    Decide siguiente nodo basado en información extraída.

    Returns:
        Nombre del nodo siguiente (debe coincidir con add_conditional_edges)
    """
    has_phone = state.get("recipient_phone") is not None
    has_amount = state.get("amount") is not None

    if has_phone and has_amount:
        return "validate"
    elif not has_phone or not has_amount:
        return "generate_response"  # Pedir información faltante

    return "continue_extracting"

def route_after_confirmation(
    state: AgentState
) -> Literal["execute", "cancel", "ask_again"]:
    """
    Analiza respuesta del usuario para confirmación.
    """
    if not state.get("awaiting_confirmation"):
        return "ask_again"

    last_message = state["messages"][-1].content.lower()

    # Palabras de confirmación
    confirm_words = ["sí", "si", "confirmo", "ok", "dale", "yes"]
    cancel_words = ["no", "cancela", "cancelar", "cancel"]

    if any(word in last_message for word in confirm_words):
        return "execute"
    elif any(word in last_message for word in cancel_words):
        return "cancel"

    return "ask_again"  # Respuesta ambigua
```

---

## 6. Persistencia con PostgreSQL {#persistencia-con-postgresql}

### Setup de PostgresSaver

```python
# apps/infrastructure/checkpointer/postgres_checkpointer.py

from langgraph.checkpoint.postgres import PostgresSaver
import asyncpg

async def setup_checkpointer(database_url: str) -> PostgresSaver:
    """
    Configura PostgresSaver para checkpointing.

    IMPORTANTE:
    - PostgresSaver crea las tablas automáticamente
    - Usa 'checkpoints' y 'checkpoint_writes' tables
    """

    # Create async pool
    pool = await asyncpg.create_pool(database_url)

    # Initialize PostgresSaver (sync connection required)
    # Para async, usar AsyncPostgresSaver
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

    checkpointer = AsyncPostgresSaver.from_conn_string(database_url)

    # Setup tables
    await checkpointer.setup()

    return checkpointer
```

### Uso en el Grafo

```python
# apps/application/agent/graph.py

from langgraph.graph import StateGraph, END

async def build_graph(checkpointer: AsyncPostgresSaver):
    """Construye el grafo con checkpointing"""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("extract", extract_information_node)
    workflow.add_node("validate", validate_transaction_node)
    workflow.add_node("confirm", confirm_transaction_node)
    workflow.add_node("execute", execute_transaction_node)
    workflow.add_node("generate_response", generate_response_node)

    # Entry point
    workflow.set_entry_point("extract")

    # Conditional edges
    workflow.add_conditional_edges(
        "extract",
        route_after_extraction,
        {
            "validate": "validate",
            "continue_extracting": "generate_response",
            "generate_response": "generate_response",
        }
    )

    workflow.add_conditional_edges(
        "confirm",
        route_after_confirmation,
        {
            "execute": "execute",
            "cancel": END,
            "ask_again": "generate_response",
        }
    )

    # Terminal edges
    workflow.add_edge("validate", "confirm")
    workflow.add_edge("execute", END)
    workflow.add_edge("generate_response", END)

    # Compile con checkpointer
    return workflow.compile(checkpointer=checkpointer)
```

### Recuperación de Estado

```python
# Invocar con thread_id para recuperar estado
config = {
    "configurable": {
        "thread_id": "user-123",
        # Opcional: checkpoint específico
        # "checkpoint_id": "abc-def-123"
    }
}

result = await graph.ainvoke(
    {"messages": [HumanMessage(content="Hola")]},
    config=config
)

# El estado se persiste automáticamente después de cada nodo
```

---

## 7. Integración con FastAPI {#integración-con-fastapi}

### Endpoint de Chat

```python
# apps/api/routes/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/api/v1", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    message: str
    stage: str
    thread_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Envía mensaje al agente y obtiene respuesta.

    El estado se persiste automáticamente usando thread_id.
    """

    # Get compiled graph (injected via dependency)
    from src.api.dependencies import get_agent_graph
    graph = await get_agent_graph()

    try:
        # Config para checkpointing
        config = {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        # Invoke graph
        # El estado anterior se recupera automáticamente
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=request.message)],
                "conversation_id": request.thread_id,
            },
            config=config
        )

        # Extraer respuesta
        last_message = result["messages"][-1].content

        return ChatResponse(
            message=last_message,
            stage=result.get("stage", "unknown"),
            thread_id=request.thread_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Streaming con Server-Sent Events

```python
from fastapi.responses import StreamingResponse
import json

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Stream agent responses en tiempo real"""

    async def event_generator():
        graph = await get_agent_graph()
        config = {"configurable": {"thread_id": request.thread_id}}

        async for event in graph.astream(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        ):
            # event es un dict con el nombre del nodo y su output
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## 8. Testing Patterns {#testing-patterns}

### Test de Nodo Individual

```python
# tests/unit/test_extract_node.py

import pytest
from langchain_core.messages import HumanMessage
from src.application.agent.nodes.extract_info import extract_information_node

@pytest.mark.asyncio
async def test_extract_phone_and_amount():
    """Test extracción exitosa de información"""

    state = {
        "messages": [
            HumanMessage(content="Enviar 50000 al 3001234567")
        ],
        "recipient_phone": None,
        "amount": None,
        "stage": "extracting_phone",
    }

    result = await extract_information_node(state)

    assert result["recipient_phone"] == "3001234567"
    assert result["amount"] == 50000.0
    assert result["stage"] == "validating"

@pytest.mark.asyncio
async def test_extract_only_phone():
    """Test extracción parcial"""

    state = {
        "messages": [HumanMessage(content="Al 3001234567")],
        "recipient_phone": None,
        "amount": None,
        "stage": "extracting_phone",
    }

    result = await extract_information_node(state)

    assert result["recipient_phone"] == "3001234567"
    assert result["amount"] is None
    assert result["stage"] == "extracting_amount"
```

### Test de Routing

```python
# tests/unit/test_routing.py

from src.application.agent.edges.routing import route_after_extraction

def test_route_to_validate_when_complete():
    """Debe ir a validar cuando tiene toda la info"""

    state = {
        "recipient_phone": "3001234567",
        "amount": 50000.0,
    }

    assert route_after_extraction(state) == "validate"

def test_route_to_continue_when_incomplete():
    """Debe continuar extrayendo si falta info"""

    state = {
        "recipient_phone": "3001234567",
        "amount": None,
    }

    assert route_after_extraction(state) == "generate_response"
```

### Test del Grafo Completo

```python
# tests/integration/test_agent_graph.py

import pytest
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_complete_transaction_flow(agent_graph, mock_checkpointer):
    """Test flujo completo de transacción"""

    config = {"configurable": {"thread_id": "test-123"}}

    # 1. Usuario inicia
    result1 = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Quiero enviar dinero")]},
        config
    )
    assert result1["stage"] == "extracting_phone"

    # 2. Usuario proporciona teléfono
    result2 = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Al 3001234567")]},
        config
    )
    assert result2["stage"] == "extracting_amount"
    assert result2["recipient_phone"] == "3001234567"

    # 3. Usuario proporciona monto
    result3 = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content="50000 pesos")]},
        config
    )
    assert result3["stage"] == "confirming"
    assert result3["amount"] == 50000.0

    # 4. Usuario confirma
    result4 = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Sí, confirmo")]},
        config
    )
    assert result4["stage"] == "completed"
    assert result4["transaction_id"] is not None
```

---

## 9. Observabilidad {#observabilidad}

### Logging Estructurado

```python
import structlog

logger = structlog.get_logger()

async def extract_information_node(state: AgentState) -> dict:
    """Nodo con logging estructurado"""

    logger.info(
        "node_execution_start",
        node="extract_information",
        thread_id=state.get("conversation_id"),
        stage=state.get("stage")
    )

    try:
        # ... lógica del nodo

        logger.info(
            "extraction_complete",
            phone=extracted.recipient_phone is not None,
            amount=extracted.amount is not None,
            next_stage=next_stage
        )

        return result

    except Exception as e:
        logger.error(
            "node_execution_failed",
            node="extract_information",
            error=str(e),
            exc_info=True
        )
        raise
```

### Métricas con Prometheus

```python
from prometheus_client import Counter, Histogram

# Definir métricas
node_executions = Counter(
    'agent_node_executions_total',
    'Total node executions',
    ['node_name', 'status']
)

node_duration = Histogram(
    'agent_node_duration_seconds',
    'Node execution duration',
    ['node_name']
)

async def extract_information_node(state: AgentState) -> dict:
    """Nodo con métricas"""

    with node_duration.labels(node_name="extract_information").time():
        try:
            result = await _extract(state)
            node_executions.labels(
                node_name="extract_information",
                status="success"
            ).inc()
            return result
        except Exception as e:
            node_executions.labels(
                node_name="extract_information",
                status="error"
            ).inc()
            raise
```

---

## 10. Patrones Avanzados {#patrones-avanzados}

### Subgrafos (Graphs dentro de Graphs)

```python
# Para flujos complejos, puedes anidar grafos

def create_validation_subgraph():
    """Subgrafo para validación compleja"""
    subgraph = StateGraph(AgentState)

    subgraph.add_node("check_format", check_format_node)
    subgraph.add_node("check_balance", check_balance_node)
    subgraph.add_node("check_limits", check_limits_node)

    subgraph.set_entry_point("check_format")
    subgraph.add_edge("check_format", "check_balance")
    subgraph.add_edge("check_balance", "check_limits")
    subgraph.add_edge("check_limits", END)

    return subgraph.compile()

# Usar en el grafo principal
workflow.add_node("validate", create_validation_subgraph())
```

### Human-in-the-Loop con Interrupción

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Compilar con interrupt_before
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute"]  # Pausar antes de ejecutar
)

# Uso
result = await graph.ainvoke(state, config)
# El grafo se detiene antes de 'execute'

# Usuario confirma externamente...

# Continuar desde donde se detuvo
final_result = await graph.ainvoke(None, config)
```

### Parallel Execution de Nodos

```python
from langgraph.graph import START, END

# Ejecutar múltiples nodos en paralelo
workflow.add_node("check_a", check_a_node)
workflow.add_node("check_b", check_b_node)
workflow.add_node("check_c", check_c_node)
workflow.add_node("aggregate", aggregate_results_node)

# Todos se ejecutan en paralelo desde START
workflow.add_edge(START, "check_a")
workflow.add_edge(START, "check_b")
workflow.add_edge(START, "check_c")

# Todos convergen en aggregate
workflow.add_edge("check_a", "aggregate")
workflow.add_edge("check_b", "aggregate")
workflow.add_edge("check_c", "aggregate")

workflow.add_edge("aggregate", END)
```

---

## 📚 Referencias

### Documentación Oficial

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Core**: https://python.langchain.com/docs/langchain_core
- **PostgresSaver**: https://langchain-ai.github.io/langgraph/how-tos/persistence_postgres/

### Ejemplos en GitHub

- LangGraph Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
- Customer Support Bot: https://github.com/langchain-ai/langgraph-example-customer-support

### Tutoriales

- Build a Customer Support Bot: https://langchain-ai.github.io/langgraph/tutorials/customer-support/
- Human-in-the-Loop: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/

---

## ✅ Checklist de Implementación

- [ ] Definir `AgentState` con TypedDict
- [ ] Crear nodos individuales (extract, validate, confirm, execute)
- [ ] Implementar funciones de routing (conditional edges)
- [ ] Configurar PostgresSaver para checkpointing
- [ ] Construir StateGraph y compilar
- [ ] Integrar con FastAPI
- [ ] Agregar logging estructurado
- [ ] Escribir tests unitarios de nodos
- [ ] Escribir tests de integración del grafo
- [ ] Documentar decisiones en ADRs

---

**Última actualización**: 2025-01-21
**Próxima revisión**: Al implementar el primer nodo
