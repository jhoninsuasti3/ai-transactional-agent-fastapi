# Documentación de Prompts - AI Transactional Agent

Este documento registra todos los prompts utilizados en el desarrollo del agente conversacional para transacciones de dinero, siguiendo los requerimientos de la prueba técnica.

## Índice

1. [Prompt de Conversación](#1-prompt-de-conversación)
2. [Prompt de Extracción](#2-prompt-de-extracción)
3. [Prompt de Validación](#3-prompt-de-validación)
4. [Prompt de Confirmación](#4-prompt-de-confirmación)
5. [Prompt de Resultado de Transacción](#5-prompt-de-resultado-de-transacción)
6. [Prompts de Desarrollo](#6-prompts-de-desarrollo)

---

## 1. Prompt de Conversación

### Contexto
Usado en el nodo `conversation` del grafo de LangGraph para guiar la interacción con el usuario y recolectar datos de la transacción.

### Ubicación
`apps/agents/transactional/prompts/conversation.py`

### Prompt Sistema

```
Eres un asistente bancario profesional y amigable que ayuda a enviar dinero.

OBJETIVO: Obtener número de celular (10 dígitos) y monto a enviar.

REGLAS:
1. Sé breve y claro
2. Pregunta UNA cosa a la vez
3. Si falta el teléfono, pregúntalo
4. Si falta el monto, pregúntalo
5. Una vez tengas ambos, confirma antes de proceder

ESTADO ACTUAL:
{% if phone %}✓ Teléfono: {{ phone }}{% else %}✗ Teléfono: Falta{% endif %}
{% if amount %}✓ Monto: ${{ amount }} COP{% else %}✗ Monto: Falta{% endif %}

Responde al usuario de forma natural y profesional.
```

### Propósito
- Mantener conversación natural y profesional
- Guiar al usuario paso a paso
- Mostrar estado actual de datos recolectados
- Optimizar para eficiencia de tokens

### Uso en Código
```python
from apps.agents.transactional.prompts.conversation import get_conversation_prompt

prompt = get_conversation_prompt(phone="3001234567", amount=50000)
# Retorna SystemMessage con template renderizado
```

### Ejemplo de Salida
```
Usuario: "Hola, quiero enviar dinero"
Agente: "¡Hola! Con gusto le ayudaré a enviar dinero. ¿A qué número de celular
         desea transferir? Recuerde que debe ser un número colombiano de 10 dígitos
         que comience con 3."
```

---

## 2. Prompt de Extracción

### Contexto
Usado en el nodo `extractor` para extraer estructuradamente el teléfono y monto de la conversación. **Nota**: En la implementación actual se usa regex en lugar de este prompt para mayor confiabilidad.

### Ubicación
`apps/agents/transactional/prompts/extractor.py`

### Prompt Sistema

```
Extrae el número de teléfono y monto de la conversación.

REGLAS:
- Teléfono: 10 dígitos exactos (ej: 3001234567)
- Monto: número positivo sin símbolos (ej: 50000)
- Si no encuentras alguno, devuelve null

CONVERSACIÓN:
{{ conversation_history }}

ÚLTIMO MENSAJE:
{{ last_message }}

Extrae los datos y devuélvelos en formato estructurado.
```

### Schema de Salida Esperado
```json
{
  "phone": "3001234567",  // string de 10 dígitos o null
  "amount": 50000         // número positivo o null
}
```

### Implementación Actual
En lugar de usar LLM, se implementó con **regex patterns** por mayor confiabilidad:

```python
# Phone: 10 digits starting with 3
phone_pattern = r'\b(3\d{9})\b'

# Amount: multiple patterns
amount_patterns = [
    r'\$\s*(\d{1,3}(?:[,.\s]?\d{3})*)',      # $75000 or $75,000
    r'(\d{1,3}(?:[,.\s]?\d{3})*)\s*pesos',   # 75000 pesos
    r'monto\s*:?\s*(\d{1,3}(?:[,.\s]?\d{3})*)',  # monto: 75000
]
```

### Razón del Cambio
- **Confiabilidad**: Regex es determinístico
- **Velocidad**: No requiere llamada al LLM
- **Costo**: Reduce uso de tokens
- **Precisión**: Evita errores de interpretación del LLM

---

## 3. Prompt de Validación

### Contexto
Usado en el nodo `validator` para interpretar resultados del API de validación y generar mensajes amigables.

### Ubicación
`apps/agents/transactional/prompts/validator.py`

### Prompt Sistema

```
Interpreta el resultado de validación y genera un mensaje al usuario.

DATOS ENVIADOS:
- Teléfono: {{ phone }}
- Monto: ${{ amount }} COP

RESULTADO VALIDACIÓN:
{{ validation_result }}

INSTRUCCIONES:
- Si es válido: Informa que la transacción puede proceder
- Si es inválido: Explica el error de forma clara y profesional
- Sé breve y directo

Genera el mensaje:
```

### Implementación
Se utiliza función helper en lugar del prompt del LLM:

```python
def get_validation_response(valid: bool, phone: str, amount: float, message: str):
    if valid:
        return f"""✅ Validación exitosa

Teléfono: {phone}
Monto: ${amount:,.0f} COP

{message}

¿Confirmas esta transacción? (Responde 'sí' para confirmar)"""
    else:
        return f"""❌ No se puede procesar la transacción

Teléfono: {phone}
Monto: ${amount:,.0f} COP

Motivo: {message}"""
```

### Ejemplo de Salidas

**Caso Exitoso:**
```
✅ Validación exitosa

Teléfono: 3001234567
Monto: $50,000 COP

La transacción puede ser procesada

¿Confirmas esta transacción? (Responde 'sí' para confirmar)
```

**Caso Fallido:**
```
❌ No se puede procesar la transacción

Teléfono: 3001234567
Monto: $50,000 COP

Motivo: Error al validar transacción: Insufficient funds
```

---

## 4. Prompt de Confirmación

### Contexto
Usado en el nodo `confirmation` para solicitar y detectar confirmación del usuario.

### Ubicación
`apps/agents/transactional/prompts/confirmation.py`

### Prompt de Solicitud

```
Genera un mensaje de confirmación claro y profesional.

DATOS:
- Teléfono: {{ phone }}
- Monto: ${{ amount }} COP

Pregunta al usuario si confirma el envío. Sé breve.
```

### Prompt de Detección

```
Determina si el usuario confirmó o canceló la transacción.

MENSAJE DEL USUARIO: {{ user_message }}

REGLAS:
- "sí", "confirmo", "adelante", "ok" → confirmed
- "no", "cancela", "espera" → cancelled
- Cualquier duda → pending

Responde solo: confirmed, cancelled o pending
```

### Lógica de Detección
El nodo detecta palabras clave de confirmación:

```python
confirmation_keywords = ["sí", "si", "confirmo", "adelante", "ok", "yes"]
cancellation_keywords = ["no", "cancela", "espera", "detener"]

if any(keyword in user_message.lower() for keyword in confirmation_keywords):
    return "confirmed"
elif any(keyword in user_message.lower() for keyword in cancellation_keywords):
    return "cancelled"
else:
    return "pending"
```

---

## 5. Prompt de Resultado de Transacción

### Contexto
Usado en el nodo `transaction` para generar mensajes de éxito o fallo.

### Ubicación
`apps/agents/transactional/prompts/transaction.py`

### Prompt Sistema

```
Genera el mensaje final de la transacción.

RESULTADO:
{{ transaction_result }}

INSTRUCCIONES:
- Si exitosa: Confirma y da el ID de transacción
- Si falló: Explica el error y sugiere qué hacer
- Sé empático y profesional
- Máximo 2 oraciones

Mensaje:
```

### Implementación
Función helper con templates fijos:

```python
def get_transaction_result_message(
    success: bool, phone: str, amount: float,
    transaction_id: str | None, message: str
):
    if success:
        return f"""✅ Transacción completada exitosamente

ID: {transaction_id}
Destino: {phone}
Monto: ${amount:,.0f} COP

{message}"""
    else:
        return f"""❌ La transacción no pudo completarse

Destino: {phone}
Monto: ${amount:,.0f} COP

Motivo: {message}

Por favor, intenta nuevamente o contacta soporte."""
```

### Ejemplos

**Transacción Exitosa:**
```
✅ Transacción completada exitosamente

ID: TXN-abc123
Destino: 3001234567
Monto: $50,000 COP

Transacción procesada correctamente
```

**Transacción Fallida:**
```
❌ La transacción no pudo completarse

Destino: 3001234567
Monto: $50,000 COP

Motivo: Service temporarily unavailable

Por favor, intenta nuevamente o contacta soporte.
```

---

## 6. Prompts de Desarrollo

### 6.1 Prompts Usados con Claude Code

Durante el desarrollo, se utilizó Claude Code (Claude Sonnet 4.5) como asistente de desarrollo. A continuación los principales prompts utilizados:

#### Prompt Inicial - Setup del Proyecto
```
Necesito implementar un agente conversacional en Python usando LangGraph que permita
realizar transacciones de envío de dinero. Los requerimientos son:

1. Stack: Python 3.12, FastAPI, LangGraph, PostgreSQL, Docker
2. El agente debe extraer: número de teléfono (10 dígitos) y monto
3. Debe validar con API mock antes de ejecutar
4. Debe pedir confirmación antes de ejecutar transacción
5. Cliente HTTP con retry pattern, circuit breaker, timeouts
6. Todo debe correr en Docker Compose

¿Por dónde empezamos?
```

#### Prompt - Estructura del Grafo
```
Necesito diseñar el grafo de LangGraph para el agente transaccional. El flujo debe ser:

1. Usuario inicia conversación
2. Agente extrae teléfono y monto
3. Valida con API
4. Pide confirmación
5. Ejecuta transacción

¿Cómo estructuramos los nodos y las transiciones condicionales?
```

#### Prompt - Resolución del Loop Infinito
```
Tengo un problema: cuando el usuario dice "Quiero enviar dinero" sin proporcionar
datos, el agente entra en loop infinito entre conversation → extract → conversation.

El error es: "Recursion limit of 25 reached"

El routing actual detecta keywords en el historial completo, entonces siempre
encuentra "enviar dinero" y va a extract, aunque no haya números.

¿Cómo lo soluciono?
```

**Solución Implementada:**
Modificar `should_extract()` para solo ir a `extract` cuando detecta patrones numéricos:
```python
has_phone_pattern = bool(re.search(r'\b3\d{9}\b', last_user_msg))
has_amount_pattern = bool(re.search(r'\$?\d+', last_user_msg))

if has_phone_pattern or has_amount_pattern:
    return "extract"
return END
```

#### Prompt - Checkpointer y Persistencia
```
El agente funciona en local pero no persiste el estado entre requests HTTP.
Cada llamada es independiente y olvida el contexto anterior.

Necesito:
1. Configurar PostgresSaver checkpointer
2. Que funcione en Docker
3. Que mantenga el estado de la conversación entre requests

¿Cómo implemento esto correctamente?
```

**Solución Implementada:**
```python
checkpointer = PostgresSaver.from_conn_string(conn_string)
with checkpointer as cp:
    cp.setup()
    agent = create_graph(checkpointer=cp)

    result = agent.invoke(
        {"messages": [HumanMessage(content=msg)]},
        config={"configurable": {"thread_id": conversation_id}}
    )
```

#### Prompt - Patrones de Resiliencia
```
Necesito implementar en el cliente HTTP:
1. Retry pattern: 3 reintentos con backoff exponencial (1s, 2s, 4s)
2. Circuit breaker: umbral 5 fallos, timeout 30s, half-open después de 60s
3. Timeouts: conexión 5s, lectura 10s
4. Logging de todas las llamadas

Usando tenacity y pybreaker. ¿Código de ejemplo?
```

#### Prompt - Error de Tool Execution
```
Tengo un error cuando el LLM llama tools:

"tool_use ids were found without tool_result blocks immediately after"

El conversation node tiene tools bind (format_phone_number_tool), pero cuando el
LLM lo llama, el tool_result no se agrega al historial de mensajes.

¿Cómo agrego un nodo de tool execution en LangGraph?
```

### 6.2 Prompts para Debugging

#### Verificar Estado del Checkpointer
```python
# Prompt para verificar si el checkpointer está guardando
SELECT * FROM checkpoint WHERE thread_id = 'conv-123'
ORDER BY checkpoint_id DESC LIMIT 5;
```

#### Inspeccionar Logs del Grafo
```
Necesito agregar logging detallado en todos los nodos de routing del grafo:
- should_extract
- should_validate
- should_confirm

Para poder debuggear dónde está el problema del loop infinito.
```

**Implementación:**
```python
logger.info(
    "should_extract_decision",
    decision="extract",
    reason="found_data_pattern",
    msg=last_user_msg[:50]
)
```

---

## 7. Optimizaciones Realizadas

### 7.1 De LLM a Regex para Extracción

**Prompt Original (Descartado):**
```
Extrae el número de teléfono y monto del siguiente mensaje:
"Enviar $50000 al 3001234567"

Devuelve JSON: {"phone": "...", "amount": ...}
```

**Cambio a Regex:**
- **Razón**: Mayor confiabilidad y menor costo
- **Resultado**: 100% precisión en extracción de patrones conocidos

### 7.2 Templates Fijos vs LLM para Respuestas

**Antes:** Usar LLM para generar cada mensaje de validación/transacción
**Después:** Templates fijos con interpolación

**Beneficios:**
- Respuestas consistentes
- Menor latencia
- Menor costo de tokens
- Fácil mantenimiento

---

## 8. Configuración de Modelos LLM

### Modelo Principal
- **Provider**: Anthropic
- **Modelo**: `claude-3-5-haiku-20241022`
- **Temperature**: 0.7
- **Max Tokens**: 500

### Configuración
```python
# apps/orchestrator/settings.py
LLM_PROVIDER = "anthropic"
LLM_MODEL = "anthropic:claude-3-5-haiku-20241022"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 500
```

### Uso en Código
```python
from apps.agents/transactional/config import get_llm

llm = get_llm()
llm_with_tools = llm.bind_tools(ALL_TOOLS)
response = llm_with_tools.invoke(messages)
```

---

## 9. Herramientas de IA Utilizadas

### Claude Code (Anthropic)
- **Modelo**: Claude Sonnet 4.5
- **Uso**: Asistente de desarrollo principal
- **Funciones**:
  - Arquitectura del grafo de LangGraph
  - Debugging de loop infinito
  - Implementación de patrones de resiliencia
  - Configuración de Docker
  - Resolución de problemas de checkpointer

### Claude API (para el Agente)
- **Modelo**: Claude 3.5 Haiku
- **Uso**: Motor del agente conversacional
- **Razón**: Balance entre costo y capacidad

---

## 10. Lecciones Aprendidas

### 10.1 Checkpointer require formato correcto
- PostgreSQL connection string debe ser `postgresql://` NO `postgresql+psycopg://`
- El checkpointer debe compilarse CON el grafo, no pasarse como parámetro de invoke

### 10.2 Routing debe evitar loops
- No basar decisiones solo en keywords del historial
- Verificar presencia de datos reales (números) antes de extraer
- Limitar recursion_limit bajo durante desarrollo (5-10)

### 10.3 Tool execution necesita nodo dedicado
- Si bind_tools al LLM, necesitas nodo que ejecute y agregue tool_results
- O quitar tools y manejar con lógica determinística

**Solución implementada**: Remover `llm.bind_tools(ALL_TOOLS)` del conversation node y manejar todo con lógica determinística (regex en extractor, templates fijos en validator/transaction).

---

## 11. Pruebas del Flujo Completo

### 11.1 Test End-to-End Exitoso

**Fecha**: 26 de Noviembre 2025
**Objetivo**: Verificar flujo completo después de arreglar error de tool execution

#### Paso 1: Inicio de Conversación

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quiero enviar dinero", "user_id": "user-test-flow"}'
```

**Response**:
```json
{
  "response": "Claro, puedo ayudarte a enviar dinero. \n\nPara comenzar, ¿cuál es el número de celular al que deseas enviar el dinero? (Por favor, proporciona un número de 10 dígitos)",
  "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce"
}
```

**Resultado**: ✅ Agente solicita teléfono correctamente

---

#### Paso 2: Proporcionar Teléfono

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "3012345678",
    "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce",
    "user_id": "user-test-flow"
  }'
```

**Response**:
```json
{
  "response": "Gracias por proporcionar el número de celular. \n\nAhora, ¿cuál es el monto que deseas enviar?",
  "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce",
  "metadata": {
    "phone": "3012345678",
    "needs_confirmation": false,
    "confirmed": false
  }
}
```

**Resultado**: ✅ Teléfono extraído y persistido, solicita monto

---

#### Paso 3: Proporcionar Monto (Paso Crítico)

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "75000 pesos",
    "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce",
    "user_id": "user-test-flow"
  }'
```

**Response**:
```json
{
  "response": "✅ Validación exitosa\n\nTeléfono: 3012345678\nMonto: $75,000 COP\n\nTransaction can be processed\n\n¿Confirmas esta transacción? (Responde 'sí' para confirmar)",
  "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce",
  "metadata": {
    "phone": "3012345678",
    "amount": 75000,
    "needs_confirmation": true,
    "confirmed": false
  }
}
```

**Resultado**: ✅ **ÉXITO** - Este paso fallaba anteriormente con error `tool_use without tool_result`
- Monto extraído correctamente
- Teléfono recordado desde paso 2 (checkpointer funcionando)
- Validación con API completada
- Solicita confirmación

---

#### Paso 4: Confirmar Transacción

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sí, confirmo",
    "conversation_id": "conv-efd9d081-f519-496c-a757-d099ed56a1ce",
    "user_id": "user-test-flow"
  }'
```

**Response**:
```json
{
  "response": "✅ Transacción completada exitosamente\n\nID: TXN-DA844534CA3A\nDestino: 3012345678\nMonto: $75,000 COP\n\nTransaction completed",
  "transaction_id": "TXN-DA844534CA3A",
  "metadata": {
    "phone": "3012345678",
    "amount": 75000,
    "needs_confirmation": true,
    "confirmed": true,
    "transaction_status": "completed"
  }
}
```

**Resultado**: ✅ Transacción ejecutada y completada exitosamente

---

### 11.2 Resumen de Verificaciones

| Componente | Estado | Evidencia |
|------------|--------|-----------|
| Conversación natural | ✅ Funciona | Respuestas claras y contextuales |
| Extracción de teléfono | ✅ Funciona | Regex detecta `3012345678` |
| Extracción de monto | ✅ Funciona | Regex detecta `75000 pesos` |
| Checkpointer (persistencia) | ✅ Funciona | Teléfono recordado en paso 3 |
| Validación API | ✅ Funciona | Mock API responde correctamente |
| Confirmación | ✅ Funciona | Detecta "Sí, confirmo" |
| Ejecución transacción | ✅ Funciona | Transaction ID generado |
| Tool execution error | ✅ Resuelto | Sin errores de `tool_use/tool_result` |

---

### 11.3 Comparación Antes/Después del Fix

**Antes (con tools binding)**:
```python
# apps/agents/transactional/nodes/conversation.py
llm = get_llm()
llm_with_tools = llm.bind_tools(ALL_TOOLS)  # ❌ Causaba error
response = llm_with_tools.invoke(messages)

# Error en paso 3:
# "tool_use ids were found without tool_result blocks immediately after"
```

**Después (sin tools binding)**:
```python
# apps/agents/transactional/nodes/conversation.py
llm = get_llm()  # ✅ Puramente conversacional
response = llm.invoke(messages)

# Paso 3 exitoso:
# Validación completada, checkpointer funcionando
```

---

## Conclusión

Este documento registra todos los prompts utilizados durante el desarrollo del agente transaccional, siguiendo el requerimiento obligatorio de documentar el uso de herramientas de IA.

**Total de Prompts Principales**: 5
**Implementaciones con Templates**: 3 (validación, confirmación, transacción)
**Implementaciones con Regex**: 1 (extracción)
**Implementaciones con LLM**: 1 (conversación)

**Pruebas Completadas**: Flujo end-to-end completo verificado exitosamente
**Fecha de Documentación**: 26 de Noviembre 2025
**Versión del Proyecto**: 1.0.0
