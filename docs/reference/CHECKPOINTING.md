# Checkpointer en LangGraph - Guía Práctica

## ¿Qué es un Checkpointer?

El checkpointer es el "sistema de memoria" de LangGraph. Permite que el agente recuerde conversaciones entre diferentes llamadas HTTP.

## Problema sin Checkpointer

```python
# Request 1
POST /api/v1/chat
{
  "message": "Hola, quiero enviar dinero",
  "user_id": "juan"
}
# Agente: "¿A qué número?"

# Request 2
POST /api/v1/chat
{
  "message": "3001234567",
  "user_id": "juan"
}
# ❌ Agente: "Hola, ¿en qué puedo ayudarte?"
# No recuerda que ya preguntó por el número!
```

## Solución con Checkpointer

```python
# Request 1
POST /api/v1/chat
{
  "message": "Hola, quiero enviar dinero",
  "user_id": "juan",
  "conversation_id": "conv-123"  # ← Clave importante
}
# Agente: "¿A qué número?"
# Checkpointer GUARDA: {thread_id: "conv-123", phone: null, amount: null}

# Request 2
POST /api/v1/chat
{
  "message": "3001234567",
  "user_id": "juan",
  "conversation_id": "conv-123"  # ← Mismo ID
}
# Checkpointer CARGA el estado anterior
# ✅ Agente: "Perfecto, ¿qué monto?"
# Checkpointer ACTUALIZA: {thread_id: "conv-123", phone: "3001234567", amount: null}
```

## Cómo Funciona Internamente

### 1. Estructura en PostgreSQL

El checkpointer crea 3 tablas:

```sql
-- Tabla principal: guarda snapshots del estado completo
CREATE TABLE checkpoint (
    thread_id TEXT,           -- "conv-123"
    checkpoint_id UUID,       -- ID único de cada snapshot
    parent_id UUID,           -- ID del checkpoint anterior
    checkpoint JSONB,         -- Estado completo: {phone, amount, messages, etc}
    metadata JSONB,           -- Info adicional
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Ejemplo de dato guardado:
{
  "thread_id": "conv-123",
  "checkpoint": {
    "messages": [
      {"role": "user", "content": "Hola"},
      {"role": "assistant", "content": "¿A qué número?"}
    ],
    "phone": null,
    "amount": null,
    "needs_confirmation": false
  }
}
```

### 2. Flujo de Ejecución

```python
# En apps/orchestrator/v1/routers/chat.py

# Paso 1: Crear checkpointer
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

# Paso 2: Compilar el grafo CON checkpointer
with checkpointer as cp:
    cp.setup()  # Crea las tablas si no existen
    agent = create_graph(checkpointer=cp)

    # Paso 3: Ejecutar con thread_id
    result = agent.invoke(
        {"messages": [HumanMessage("3001234567")]},
        config={
            "configurable": {
                "thread_id": "conv-123"  # ← El agente busca estado previo con este ID
            }
        }
    )

    # Internamente:
    # 1. Checkpointer busca en PostgreSQL: SELECT * FROM checkpoint WHERE thread_id='conv-123'
    # 2. Carga el estado anterior (phone=null, amount=null, messages=[...])
    # 3. Agrega el nuevo mensaje: messages.append(HumanMessage("3001234567"))
    # 4. Ejecuta el grafo con ese estado
    # 5. Extrae phone="3001234567"
    # 6. GUARDA el nuevo estado: INSERT INTO checkpoint (thread_id, checkpoint, ...) VALUES (...)
```

## Analogía del Mundo Real

Imagina que cada conversación es un **expediente físico**:

### Sin Checkpointer (Sin expediente)
- Cliente llama: "Hola, quiero un crédito"
- Empleado: "Bien, ¿cuál es tu nombre?"
- Cliente cuelga y vuelve a llamar: "Juan Pérez"
- Otro empleado: "Hola, ¿en qué puedo ayudarte?" ❌
- No hay registro de la conversación anterior

### Con Checkpointer (Con expediente)
- Cliente llama: "Hola, quiero un crédito"
- Empleado escribe en expediente #123: "Cliente quiere crédito"
- Empleado: "Bien, ¿cuál es tu nombre?"
- Cliente cuelga y vuelve a llamar con expediente #123
- Empleado lee expediente: "Ah sí, estabas pidiendo un crédito"
- Empleado: "Perfecto Juan, ¿cuánto necesitas?" ✅

## Código Real en Nuestro Proyecto

### Cuando el usuario envía un mensaje:

```python
# apps/orchestrator/v1/routers/chat.py:48-74

# 1. Usuario envía mensaje con conversation_id
conversation_id = "conv-abc-123"

# 2. Creamos checkpointer
checkpointer_cm = PostgresSaver.from_conn_string(settings.LANGGRAPH_CHECKPOINT_DB)

# 3. Usamos contexto para manejar conexión a PostgreSQL
with checkpointer_cm as checkpointer:
    # 4. Setup crea tablas si es primera vez
    checkpointer.setup()

    # 5. Compilamos grafo CON checkpointer
    agent = get_agent(checkpointer=checkpointer)

    # 6. Preparamos solo el NUEVO mensaje (no todo el historial)
    input_data = {
        "messages": [HumanMessage(content="3001234567")]
    }

    # 7. Config con thread_id = conversation_id
    config = {
        "configurable": {
            "thread_id": conversation_id  # ← Busca/guarda en PostgreSQL con este ID
        },
        "recursion_limit": 5
    }

    # 8. Invoke ejecuta:
    #    a) Busca estado previo en PostgreSQL con thread_id
    #    b) Si existe, lo carga (messages anteriores, phone, amount, etc)
    #    c) Agrega el nuevo mensaje
    #    d) Ejecuta el grafo
    #    e) Guarda el nuevo estado en PostgreSQL
    result = agent.invoke(input_data, config=config)
```

## Beneficios del Checkpointer

1. **Memoria Persistente**: Sobrevive a reinicios del servidor
2. **Multi-turno**: Permite conversaciones de múltiples mensajes
3. **Recuperación**: Si el servidor falla, puede retomar
4. **Auditoría**: Tienes historial completo en BD
5. **Concurrencia**: Múltiples usuarios con sus propias conversaciones

## Limitación Sin Checkpointer (Local)

Cuando corremos localmente sin checkpointer:

```python
# Cada request es INDEPENDIENTE
agent = get_agent(checkpointer=None)

# Request 1
result = agent.invoke({"messages": [HumanMessage("Hola")]})
# Estado: {phone: null, amount: null}

# Request 2 - Estado se PERDIÓ
result = agent.invoke({"messages": [HumanMessage("3001234567")]})
# Estado: {phone: null, amount: null}  ← Empieza de cero!
```

## Conclusión

El checkpointer es esencial para:
- ✅ Conversaciones multi-turno
- ✅ Mantener contexto entre requests
- ✅ Flujo conversacional natural
- ✅ Extracción incremental de datos

Sin él, el agente tiene "amnesia" entre cada request HTTP.
