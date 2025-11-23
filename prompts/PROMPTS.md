# Registro de Prompts Utilizados

> **OBLIGATORIO**: Este documento registra TODOS los prompts utilizados durante el desarrollo del proyecto,
> tanto para asistencia de desarrollo (Claude) como para el sistema en producción (OpenAI).

**Última actualización**: 2025-01-21
**Versión del documento**: 1.0.0

---

## 📋 Índice

1. [Información General](#información-general)
2. [Prompts de Desarrollo - Claude](#prompts-desarrollo-claude)
3. [Prompts del Sistema - OpenAI](#prompts-sistema-openai)
4. [Comparación y Análisis](#comparación-y-análisis)
5. [Optimizaciones de Tokens](#optimizaciones-de-tokens)
6. [Versionado de Prompts](#versionado-de-prompts)
7. [Apéndices](#apéndices)

---

## 1. Información General {#información-general}

### Propósito del Documento

Este documento cumple con el requisito obligatorio de la prueba técnica de documentar todos los prompts utilizados.
Se divide en dos categorías principales:

1. **Prompts de Desarrollo (Claude)**: Usados para asistencia en desarrollo, arquitectura, debugging
2. **Prompts del Sistema (OpenAI)**: Usados en producción para el agente conversacional

### Metodología de Registro

Para cada prompt se documenta:
- **Contexto**: ¿Por qué se usó este prompt?
- **Fecha y hora**: Cuándo se utilizó
- **Prompt completo**: Texto exacto del prompt
- **Resultado**: Qué se obtuvo
- **Tokens estimados**: Consumo aproximado (cuando aplique)
- **Iteraciones**: Versiones anteriores y mejoras

### Herramientas Utilizadas

- **Claude Code** (Anthropic): Asistencia de desarrollo (este documento)
- **OpenAI API**: Sistema en producción
  - Modelos disponibles: gpt-4.1-mini, gpt-4.1-nano, gpt-5-mini, gpt-5-nano
  - Modelo seleccionado: **gpt-4.1-mini** (balance precio/rendimiento)

---

## 2. Prompts de Desarrollo - Claude {#prompts-desarrollo-claude}

> **Nota**: Claude se usa SOLO para desarrollo asistido, NO en producción.
> No consume la API Key de OpenAI proporcionada.

### 2.1 Análisis Inicial y Planificación

#### 2.1.1 Análisis de Requerimientos

**Fecha**: 2025-01-21 [Hora inicial]
**Contexto**: Análisis exhaustivo de la prueba técnica y generación del plan de trabajo

**Prompt**:
```
Seras mi asistente para el desarrollo de la prueba que te voy a pasar, el LLm sera
open ai porque asi lo eligieron cuando me compartieron el reto, de momento solo haz
un analisis, actua como un experto en desarrollo de software, en ai, en agentes y
arquitectura de software, y devops.

Quiero que me entregues un plan detallado, te voy a pasar tambien un proyecto que es
un poco viejo para el desarrollo de este tipo de sistemas que esta en la raiz con el
nombre de /home/jhonmo/apps/retos/ai-transactional-agent-fastapi/api-gabi-logic,
ademas te paso contexto que genere con herramientas y tools diferentes a anthropic o
claude, tambien podrian ser utiles
(/home/jhonmo/apps/retos/ai-transactional-agent-fastapi/docs/CONTEXTO.md) y en
general toda la documentacion la idea es dejarla alli, con excepcion al readme del
proyecto.

Recuerda hazme un plan de accion y bien estructurado, como si fuese un proyecto
enterprise, y profesional, profundiza en proyectos parecidos o similiares y el buen
uso de patrones y arquitecturas en terminos de desarrollo y de agentes
```

**Archivos leídos**:
- `/home/jhonmo/apps/retos/ai-transactional-agent-fastapi/docs/CONTEXTO.md`
- `/home/jhonmo/apps/retos/ai-transactional-agent-fastapi/PRUEBA_TECNICA_AI_AGENT.md`
- `/home/jhonmo/apps/retos/ai-transactional-agent-fastapi/api-gabi-logic/` (varios archivos)

**Resultado**:
- Análisis completo de requerimientos
- Comparación LangChain vs LangGraph
- Evaluación del proyecto legacy (api-gabi-logic)
- Plan de 5 días con estructura detallada
- Arquitectura hexagonal propuesta
- Stack tecnológico moderno recomendado

**Tokens utilizados**: ~8,000 tokens (estimado, contexto amplio)

**Aprendizajes**:
- Proyecto legacy usa LangChain 0.0.330 (obsoleto)
- LangGraph es superior para agentes transaccionales
- Necesidad de patrones de resiliencia explícitos
- Arquitectura hexagonal encaja perfectamente

---

#### 2.1.2 Refinamiento del Plan

**Fecha**: 2025-01-21
**Contexto**: Ajuste del plan inicial a 5 días de desarrollo

**Prompt**:
```
Pues la idea es testear muy bien todo, primero guardame el plan de trabajo y fases,
pero antes recuerda que tenemos 5 dias para poder realizar el proyecto por lo que
podemos estructuralo, organizarlo y testearlo correctamente, con las ultimas
caracteristicas usadas en el mercado laboral, ademas recuerda que en el requerimiento
piden explicitamente dejar registro de los prompts utilizados y demas, ademas tengo
al key de open ai, pero creo que es limitada, asi que primero voy a probar con claude,
dejar aparte los prompts o cosas que me genere uno vs otro
```

**Resultado**:
- Plan de trabajo extendido a 5 días (este documento)
- Estructura detallada día por día
- Énfasis en testing (>70% coverage)
- Sistema de tracking de prompts (este archivo)
- Estrategia de uso: Claude para dev, OpenAI para producción

**Tokens utilizados**: ~12,000 tokens (incluyendo generación del plan)

**Decisiones tomadas**:
1. Usar Claude para desarrollo asistido
2. Usar OpenAI gpt-4.1-mini para producción
3. Documentar TODOS los prompts en este archivo
4. Crear estructura de tracking separada por LLM

---

### 2.2 Diseño de Arquitectura

#### 2.2.1 [A completar durante el desarrollo]

**Fecha**: [Pendiente]
**Contexto**: [Descripción]
**Prompt**:
```
[Prompt exacto]
```
**Resultado**: [Descripción]
**Tokens**: [Estimado]

---

### 2.3 Implementación de Componentes

#### 2.3.1 [A completar durante el desarrollo]

**Fecha**: [Pendiente]
**Contexto**: [Descripción]
**Prompt**:
```
[Prompt exacto]
```
**Resultado**: [Descripción]
**Tokens**: [Estimado]

---

### 2.4 Debugging y Optimización

#### 2.4.1 [A completar durante el desarrollo]

**Fecha**: [Pendiente]
**Contexto**: [Descripción]
**Prompt**:
```
[Prompt exacto]
```
**Resultado**: [Descripción]
**Tokens**: [Estimado]

---

### 2.5 Refactoring y Code Review

#### 2.5.1 [A completar durante el desarrollo]

**Fecha**: [Pendiente]
**Contexto**: [Descripción]
**Prompt**:
```
[Prompt exacto]
```
**Resultado**: [Descripción]
**Tokens**: [Estimado]

---

## 3. Prompts del Sistema - OpenAI {#prompts-sistema-openai}

> **Nota**: Estos prompts se ejecutan en producción y consumen la API Key proporcionada.
> **CRÍTICO**: Optimizar para minimizar consumo de tokens (límite 100K).

### 3.1 System Prompts

#### 3.1.1 System Prompt Principal del Agente

**Versión**: 1.0.0
**Fecha creación**: [A definir]
**Modelo**: gpt-4.1-mini
**Temperatura**: 0
**Max tokens respuesta**: 500

**Prompt**:
```python
SYSTEM_PROMPT_V1 = """
Eres un asistente bancario amigable y profesional especializado en procesar
envíos de dinero en Colombia.

## Tu Objetivo
Extraer la siguiente información del usuario de forma conversacional:
1. Número de teléfono del destinatario (10 dígitos)
2. Monto a enviar (en pesos colombianos, debe ser mayor a 0)

## Reglas Importantes
- Sé conciso y claro. Máximo 2-3 oraciones por respuesta.
- NO hagas suposiciones sobre datos no proporcionados
- Si falta información, pregunta UNA cosa a la vez
- Valida el formato antes de pedir confirmación
- Maneja errores con empatía y claridad

## Validaciones
- Teléfono: Exactamente 10 dígitos, comenzando con 3
- Monto: Número positivo mayor a 0

## Formato de Respuesta
- Tono: Profesional pero amigable
- Longitud: Concisa (2-3 oraciones)
- No uses emojis
- Confirma los datos antes de proceder

## Ejemplos de Interacción
User: "Quiero enviar dinero"
Assistant: "Con gusto te ayudo. ¿A qué número de celular deseas enviar el dinero?"

User: "Al 3001234567"
Assistant: "Perfecto, 3001234567. ¿Qué monto deseas enviar?"

User: "50000 pesos"
Assistant: "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?
Responde 'Sí, confirmo' para proceder o 'No' para cancelar."

## Manejo de Errores
- Teléfono inválido: "El número debe tener 10 dígitos y comenzar con 3.
  ¿Podrías verificarlo?"
- Monto inválido: "El monto debe ser mayor a 0. ¿Cuánto deseas enviar?"
"""
```

**Estimación de tokens**: ~350 tokens

**Justificación del diseño**:
- Estructura clara con secciones
- Ejemplos concretos para few-shot learning
- Validaciones explícitas
- Manejo de errores predefinido
- Longitud controlada para reducir tokens

**Iteraciones**:
- v1.0.0: Versión inicial

---

#### 3.1.2 Prompt de Extracción Estructurada

**Versión**: 1.0.0
**Fecha creación**: [A definir]
**Modelo**: gpt-4.1-mini
**Uso**: Function calling para extraer datos

**Función Definida**:
```python
EXTRACTION_FUNCTION = {
    "name": "extract_transaction_info",
    "description": "Extrae información de transacción del mensaje del usuario",
    "parameters": {
        "type": "object",
        "properties": {
            "recipient_phone": {
                "type": "string",
                "description": "Número de teléfono de 10 dígitos, solo números",
                "pattern": "^3[0-9]{9}$"
            },
            "amount": {
                "type": "number",
                "description": "Monto a enviar en pesos colombianos, debe ser mayor a 0",
                "minimum": 1
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Confianza en la extracción"
            }
        }
    }
}
```

**Prompt de contexto para function calling**:
```python
EXTRACTION_CONTEXT = """
Del mensaje del usuario, extrae la información disponible.
Si un campo no está presente o no estás seguro, devuelve null.

Reglas de parsing:
- Teléfono: Normaliza removiendo espacios, guiones, paréntesis
  Ejemplos: "300-123-4567" → "3001234567", "300 123 4567" → "3001234567"
- Monto: Acepta formatos como "50000", "50 mil", "cincuenta mil"
  Conversiones: "mil" = 1000, "millón" = 1000000
- Confidence:
  - high: Datos claros y validables
  - medium: Datos presentes pero ambiguos
  - low: Datos posiblemente incorrectos

NO inventes datos. Si hay duda, marca confidence como "low".
"""
```

**Estimación de tokens**: ~200 tokens

**Ventajas del approach**:
- Function calling reduce tokens vs parsing manual
- Respuestas estructuradas (JSON)
- Validación automática de tipos
- Confianza explícita

---

#### 3.1.3 Prompt de Confirmación

**Versión**: 1.0.0
**Fecha creación**: [A definir]
**Modelo**: gpt-4.1-mini
**Uso**: Generar mensaje de confirmación

**Template**:
```python
CONFIRMATION_TEMPLATE = """
Genera un mensaje de confirmación profesional y claro para una transacción de
envío de dinero con los siguientes datos:

- Número destinatario: {recipient_phone}
- Monto: ${amount:,.0f} COP

Requisitos:
1. Confirma los datos de forma clara
2. Pide confirmación explícita
3. Menciona las opciones: "Sí, confirmo" o "No, cancelar"
4. Máximo 2-3 oraciones
5. Tono profesional pero amigable

NO agregues información adicional como comisiones o tiempos (eso no es parte
del scope).
"""
```

**Ejemplo de output esperado**:
```
"Entendido. Confirmas el envío de $50,000 COP al número 3001234567?
Por favor responde 'Sí, confirmo' para proceder o 'No' para cancelar la operación."
```

**Estimación de tokens**: ~150 tokens (template) + ~50 tokens (output)

---

### 3.2 Prompts para Manejo de Errores

#### 3.2.1 Prompt para Errores de Validación

**Versión**: 1.0.0
**Fecha creación**: [A definir]

**Template**:
```python
ERROR_HANDLING_PROMPT = """
El usuario proporcionó datos inválidos. Genera un mensaje de error amigable.

Error: {error_type}
Valor proporcionado: {provided_value}
Expectativa: {expected_format}

Requisitos:
1. Explica el error de forma clara y simple
2. Indica qué se esperaba
3. Pide que lo intente de nuevo
4. Mantén tono empático (no culpes al usuario)
5. Máximo 2 oraciones

Tipos de error:
- invalid_phone: Teléfono no tiene 10 dígitos o no empieza con 3
- invalid_amount: Monto es 0, negativo o no es un número
- missing_data: Falta información requerida
"""
```

**Ejemplos de outputs**:
```python
# invalid_phone
"El número debe tener 10 dígitos y comenzar con 3. ¿Podrías verificar el número?"

# invalid_amount
"El monto debe ser mayor a 0. ¿Cuánto deseas enviar?"

# missing_data
"Para completar el envío necesito el número del destinatario. ¿A qué número
deseas enviar?"
```

**Estimación de tokens**: ~100 tokens (template) + ~40 tokens (output)

---

#### 3.2.2 Prompt para Fallos de API Externa

**Versión**: 1.0.0
**Fecha creación**: [A definir]

**Template**:
```python
API_ERROR_PROMPT = """
Ocurrió un error al procesar la transacción con el servicio externo.

Error técnico: {technical_error}
Acción que se intentó: {action}

Genera un mensaje para el usuario que:
1. Explique que hubo un problema temporal
2. NO revele detalles técnicos
3. Indique qué puede hacer (reintentar, esperar, contactar soporte)
4. Mantenga la calma y profesionalismo
5. Máximo 2 oraciones

El usuario NO debe ver el error técnico.
"""
```

**Ejemplos de outputs**:
```python
# Timeout
"Lo siento, hubo un problema temporal al procesar tu solicitud.
¿Podrías intentarlo nuevamente?"

# Service unavailable
"El servicio de transacciones está temporalmente no disponible.
Por favor intenta en unos minutos."

# Circuit breaker open
"Estamos experimentando problemas técnicos temporales.
Por favor intenta más tarde o contacta a soporte."
```

**Estimación de tokens**: ~120 tokens (template) + ~50 tokens (output)

---

### 3.3 Prompts para Features Avanzados (Opcional)

#### 3.3.1 Prompt para Detección de Intención

**Versión**: 1.0.0
**Fecha creación**: [A definir]
**Uso**: Clasificar intención del usuario (opcional, si sobra presupuesto de tokens)

**Prompt**:
```python
INTENT_CLASSIFICATION_PROMPT = """
Clasifica la intención del usuario en UNA de las siguientes categorías:

Categorías:
- start_transaction: Quiere iniciar un envío de dinero
- provide_phone: Está dando el número de teléfono
- provide_amount: Está dando el monto
- confirm: Está confirmando la transacción
- cancel: Quiere cancelar
- ask_status: Pregunta por el estado de una transacción
- help: Pide ayuda o información
- out_of_scope: Mensaje fuera del alcance del sistema

Mensaje del usuario: {user_message}

Responde SOLO con la categoría, sin explicación.
"""
```

**Nota**: Este prompt es OPCIONAL y solo se usaría si tenemos presupuesto de tokens
sobrante. La extracción con function calling ya maneja la mayoría de casos.

**Estimación de tokens**: ~150 tokens (probablemente no se use)

---

## 4. Comparación y Análisis {#comparación-y-análisis}

### 4.1 Claude vs OpenAI: Características

| Aspecto | Claude (Anthropic) | OpenAI |
|---------|-------------------|---------|
| **Contexto** | 200K tokens | 128K tokens (gpt-4.1-mini) |
| **Costo** | ~$3/M tokens input | ~$0.15/M tokens (mini) |
| **Velocidad** | Moderada | Rápida |
| **Function calling** | Limitado | Excelente |
| **Razonamiento** | Excelente | Muy bueno |
| **Disponibilidad API** | Limited preview | GA (Generally Available) |
| **Rate limits** | Más restrictivos | Generosos |

### 4.2 Decisión de Uso

#### Para Desarrollo (Claude)

**✅ Usar Claude para**:
- Diseño de arquitectura
- Refactoring de código
- Explicaciones detalladas
- Generación de documentación
- Code review
- Debugging complejo

**Justificación**:
- Contexto amplio permite entender todo el proyecto
- Excelente para razonamiento arquitectónico
- No consume API Key de OpenAI (limitada)

#### Para Producción (OpenAI)

**✅ Usar OpenAI gpt-4.1-mini para**:
- Procesamiento de mensajes del usuario
- Extracción de información
- Generación de respuestas
- Clasificación de intenciones

**Justificación**:
1. API Key proporcionada por el evaluador
2. gpt-4.1-mini es 10x más barato que gpt-4
3. Function calling robusto y confiable
4. Suficiente para el scope del agente
5. Rate limits adecuados para la prueba

### 4.3 ¿Por qué NO gpt-4.1-nano?

Aunque gpt-4.1-nano es aún más barato:
- ❌ Menos capacidad de razonamiento
- ❌ Contexto más limitado (64K)
- ❌ Peor performance en extracción compleja

**Decisión**: gpt-4.1-mini ofrece mejor balance precio/calidad para este caso de uso.

---

## 5. Optimizaciones de Tokens {#optimizaciones-de-tokens}

### 5.1 Límite de Tokens

**Disponible**: 100,000 tokens totales
**Estrategia**: Usar de forma conservadora

### 5.2 Estrategias de Optimización Implementadas

#### 5.2.1 Truncado de Historial

```python
# Implementación en código
MAX_MESSAGES_IN_HISTORY = 10  # Últimos 10 mensajes solamente

def truncate_conversation_history(messages: list) -> list:
    """
    Mantiene solo los últimos N mensajes para reducir tokens.
    System prompt + últimos 10 mensajes usuario/asistente.
    """
    if len(messages) <= MAX_MESSAGES_IN_HISTORY:
        return messages

    # Siempre mantener el system prompt
    system_messages = [m for m in messages if m["role"] == "system"]
    other_messages = [m for m in messages if m["role"] != "system"]

    # Últimos N mensajes
    recent_messages = other_messages[-MAX_MESSAGES_IN_HISTORY:]

    return system_messages + recent_messages
```

**Ahorro**: ~50% de tokens en conversaciones largas

---

#### 5.2.2 Summarization de Conversaciones Largas

```python
# Si conversación > 20 mensajes, resumir los primeros 10
MAX_BEFORE_SUMMARIZATION = 20

def maybe_summarize_conversation(messages: list) -> list:
    """
    Si hay más de 20 mensajes, resume los primeros 10 en un solo mensaje.
    """
    if len(messages) <= MAX_BEFORE_SUMMARIZATION:
        return messages

    messages_to_summarize = messages[:10]
    recent_messages = messages[10:]

    # Usar gpt-4.1-mini para resumir (más barato)
    summary = summarize_messages(messages_to_summarize)

    return [
        {"role": "system", "content": f"Resumen de conversación previa: {summary}"}
    ] + recent_messages
```

**Ahorro**: ~60% de tokens en conversaciones muy largas (>20 mensajes)

---

#### 5.2.3 System Prompt Conciso

- ❌ **Evitar**: Ejemplos exhaustivos, repeticiones, explicaciones largas
- ✅ **Preferir**: Bullets, secciones claras, ejemplos mínimos

**Comparación**:
```python
# ❌ Prompt verbose (500 tokens)
VERBOSE_PROMPT = """
Eres un asistente muy amigable y servicial que trabaja para un banco...
[muchas explicaciones repetitivas]
"""

# ✅ Prompt conciso (350 tokens)
CONCISE_PROMPT = """
Eres un asistente bancario que procesa envíos de dinero.

Objetivo: Extraer teléfono (10 dígitos) y monto (>0).
Reglas: Conciso, sin suposiciones, valida datos.
"""
```

**Ahorro**: 30% en system prompt

---

#### 5.2.4 Function Calling vs Text Parsing

```python
# ❌ Parsing de texto (consume más tokens)
response = llm.invoke(
    "Extrae el teléfono y monto del siguiente texto: ..."
)
# Respuesta: "El teléfono es 3001234567 y el monto es 50000" (más tokens)

# ✅ Function calling (estructurado, menos tokens)
response = llm.invoke(
    messages,
    functions=[extract_transaction_info]
)
# Respuesta: {"recipient_phone": "3001234567", "amount": 50000} (menos tokens)
```

**Ahorro**: ~40% en respuestas estructuradas

---

### 5.3 Métricas de Consumo

#### Estimación por Conversación Completa

```
┌─────────────────────────────────────────────────────┐
│  CONVERSACIÓN COMPLETA (5 turnos usuario/asistente) │
├─────────────────────────────────────────────────────┤
│  System prompt:            350 tokens               │
│  Historial (10 msgs):      400 tokens               │
│  User input (promedio):     30 tokens x 5 = 150     │
│  Assistant output:         200 tokens x 5 = 1000    │
│  Function calls:           100 tokens x 3 = 300     │
├─────────────────────────────────────────────────────┤
│  TOTAL POR CONVERSACIÓN:  ~2,200 tokens             │
└─────────────────────────────────────────────────────┘

Con 100,000 tokens disponibles:
- Conversaciones completas posibles: ~45
- Margen de seguridad (20%): ~36 conversaciones
```

#### Alertas de Consumo

Implementar alertas cuando se alcance:

```python
TOKEN_ALERTS = {
    "warning": 50_000,   # 50% consumido
    "critical": 75_000,  # 75% consumido
    "emergency": 90_000  # 90% consumido
}

def check_token_usage(tokens_used: int):
    if tokens_used >= TOKEN_ALERTS["emergency"]:
        log.error("EMERGENCY: 90% tokens consumidos")
        # Considerar desactivar features opcionales
    elif tokens_used >= TOKEN_ALERTS["critical"]:
        log.warning("CRITICAL: 75% tokens consumidos")
    elif tokens_used >= TOKEN_ALERTS["warning"]:
        log.info("WARNING: 50% tokens consumidos")
```

---

#### Monitoreo en Tiempo Real

```python
# Implementar endpoint de métricas
@app.get("/api/v1/metrics/tokens")
async def get_token_metrics():
    return {
        "total_available": 100_000,
        "total_used": get_tokens_used_from_db(),
        "remaining": 100_000 - get_tokens_used_from_db(),
        "percentage_used": (get_tokens_used_from_db() / 100_000) * 100,
        "estimated_conversations_remaining": (100_000 - get_tokens_used_from_db()) / 2200
    }
```

---

### 5.4 Plan B: Si se Agotan los Tokens

Si nos quedamos sin tokens de OpenAI:

1. **Opción 1**: Usar Claude API (si está disponible)
   - Requiere API key propia
   - Más caro pero funcional

2. **Opción 2**: Usar modelos locales
   - Llama 3.1 (8B) vía Ollama
   - Gratis pero requiere ajustar prompts
   - Menor calidad

3. **Opción 3**: Mocks para tests
   - Respuestas predefinidas
   - Solo para demostración
   - NO recomendado (no es funcional)

**Prioridad**: Optimizar para NO tener que usar Plan B.

---

## 6. Versionado de Prompts {#versionado-de-prompts}

### 6.1 Estrategia de Versionado

Todos los prompts siguen semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Cambios que rompen compatibilidad (cambio de estructura)
- **MINOR**: Agregar funcionalidad (nuevas secciones, ejemplos)
- **PATCH**: Correcciones menores (typos, optimizaciones)

### 6.2 Historial de Versiones

#### System Prompt Principal

| Versión | Fecha | Cambios | Impacto Tokens | Razón |
|---------|-------|---------|----------------|-------|
| 1.0.0 | [TBD] | Versión inicial | Baseline | Implementación inicial |

*(Se actualizará durante el desarrollo)*

---

#### Prompt de Extracción

| Versión | Fecha | Cambios | Impacto Tokens | Razón |
|---------|-------|---------|----------------|-------|
| 1.0.0 | [TBD] | Versión inicial | Baseline | Implementación inicial |

*(Se actualizará durante el desarrollo)*

---

### 6.3 Testing de Prompts

Cada versión de prompt debe probarse con:

```python
# tests/prompts/test_system_prompt.py

PROMPT_TEST_CASES = [
    {
        "user_message": "Quiero enviar dinero",
        "expected_intent": "start_transaction",
        "expected_asks_for": "phone"
    },
    {
        "user_message": "Al 3001234567",
        "expected_extraction": {"recipient_phone": "3001234567"},
        "expected_asks_for": "amount"
    },
    {
        "user_message": "50000 pesos",
        "expected_extraction": {"amount": 50000},
        "expected_asks_for": "confirmation"
    },
    {
        "user_message": "Sí confirmo",
        "expected_action": "execute_transaction"
    }
]

def test_prompt_consistency():
    """Verifica que el prompt produce resultados consistentes"""
    for test_case in PROMPT_TEST_CASES:
        # Ejecutar 5 veces el mismo prompt
        results = [
            run_prompt(test_case["user_message"])
            for _ in range(5)
        ]
        # Verificar consistencia >80%
        assert consistency_score(results) > 0.8
```

---

## 7. Apéndices {#apéndices}

### Apéndice A: Ejemplos de Conversaciones Completas

#### A.1 Flujo Exitoso

```
[SYSTEM]: [System prompt v1.0.0]

[USER]: Hola, quiero enviar dinero

[ASSISTANT]: Con gusto te ayudo. ¿A qué número de celular deseas enviar el dinero?

[USER]: Al 3001234567

[ASSISTANT]: Perfecto, 3001234567. ¿Qué monto deseas enviar?

[USER]: 50000 pesos

[ASSISTANT]: Entendido. Confirmas el envío de $50,000 COP al número 3001234567?
Responde 'Sí, confirmo' para proceder o 'No' para cancelar.

[USER]: Sí, confirmo

[ASSISTANT]: Transacción completada exitosamente. El ID de tu transacción es:
TXN-20250121143022-4582. Hemos enviado $50,000 COP al número 3001234567.

[TOKENS ESTIMADOS]: ~2,100 tokens
```

---

#### A.2 Manejo de Error: Teléfono Inválido

```
[SYSTEM]: [System prompt v1.0.0]

[USER]: Quiero enviar plata

[ASSISTANT]: Con gusto. ¿A qué número de celular deseas enviar el dinero?

[USER]: Al 123456

[ASSISTANT]: El número debe tener 10 dígitos y comenzar con 3. ¿Podrías verificarlo?

[USER]: Perdón, es 3001234567

[ASSISTANT]: Perfecto, 3001234567. ¿Qué monto deseas enviar?

[TOKENS ESTIMADOS]: ~1,800 tokens
```

---

#### A.3 Cancelación de Usuario

```
[SYSTEM]: [System prompt v1.0.0]

[USER]: Quiero enviar dinero

[ASSISTANT]: Con gusto te ayudo. ¿A qué número de celular deseas enviar el dinero?

[USER]: Al 3001234567

[ASSISTANT]: Perfecto, 3001234567. ¿Qué monto deseas enviar?

[USER]: 100000 pesos

[ASSISTANT]: Entendido. Confirmas el envío de $100,000 COP al número 3001234567?
Responde 'Sí, confirmo' para proceder o 'No' para cancelar.

[USER]: No, mejor no

[ASSISTANT]: Entendido, he cancelado la transacción. ¿Hay algo más en lo que
pueda ayudarte?

[TOKENS ESTIMADOS]: ~2,000 tokens
```

---

### Apéndice B: Herramientas de Monitoreo

#### B.1 Script de Conteo de Tokens

```python
# scripts/count_tokens.py

import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Cuenta tokens para un texto dado"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_conversation_cost(messages: list) -> dict:
    """Estima costo de una conversación"""
    total_tokens = sum(count_tokens(m["content"]) for m in messages)

    # Precios gpt-4.1-mini (input)
    cost_per_million = 0.15
    cost = (total_tokens / 1_000_000) * cost_per_million

    return {
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
        "remaining_budget": 100_000 - total_tokens
    }
```

---

#### B.2 Dashboard de Métricas

```python
# src/api/routes/monitoring.py

@app.get("/monitoring/prompts")
async def get_prompt_metrics():
    """Dashboard de uso de prompts"""
    return {
        "prompts": {
            "system_prompt": {
                "version": "1.0.0",
                "tokens": 350,
                "usage_count": get_usage_count("system_prompt")
            },
            "extraction_prompt": {
                "version": "1.0.0",
                "tokens": 200,
                "usage_count": get_usage_count("extraction_prompt")
            }
        },
        "global_metrics": {
            "total_tokens_used": get_total_tokens(),
            "total_conversations": get_conversation_count(),
            "avg_tokens_per_conversation": get_avg_tokens(),
            "budget_remaining_percentage": get_budget_percentage()
        }
    }
```

---

### Apéndice C: Checklist de Prompts

Antes de deployar un nuevo prompt:

- [ ] Testeado con al menos 10 casos de prueba
- [ ] Medido consumo de tokens
- [ ] Documentado en este archivo
- [ ] Versionado correctamente
- [ ] Comparado con versión anterior (si aplica)
- [ ] Revisado por al menos una persona
- [ ] Incluido en suite de tests automáticos

---

### Apéndice D: Referencias y Recursos

#### Documentación Oficial

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Tiktoken (token counting)](https://github.com/openai/tiktoken)
- [Best Practices for Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)

#### Artículos y Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)
- [Constitutional AI](https://www.anthropic.com/index/constitutional-ai-harmlessness-from-ai-feedback)

---

## 📝 Notas Finales

### Sobre Este Documento

Este documento es **OBLIGATORIO** según los requerimientos de la prueba técnica.
Se actualiza continuamente durante el desarrollo del proyecto.

### Cómo Contribuir

Durante el desarrollo, cada vez que uses un prompt:

1. Agrega una entrada en la sección correspondiente
2. Incluye contexto, prompt completo, y resultado
3. Estima tokens consumidos
4. Documenta decisiones tomadas

### Versionado del Documento

- **Versión actual**: 1.0.0
- **Última actualización**: 2025-01-21
- **Próxima revisión**: Al finalizar Día 1

---

**Fin del documento**
