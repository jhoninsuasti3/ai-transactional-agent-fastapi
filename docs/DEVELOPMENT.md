# Guía de Desarrollo - AI Transactional Agent

> Plan de desarrollo, estado actual y roadmap del proyecto

---

## 📊 Estado Actual del Proyecto

**Última actualización**: 2025-01-23
**Fase actual**: Arquitectura Base Completada → Implementación de APIs
**Progreso global**: 60% (Infraestructura ✅, Implementación ⏸️)

### ✅ Completado (100%)

#### 1. Estructura Enterprise
- ✅ `apps/agents/` - Agentes modulares con LangGraph
- ✅ `apps/orchestrator/` - Backend completo (API, config, servicios)
- ✅ Separación clara de responsabilidades
- ✅ Preparado para escalar horizontalmente

#### 2. Configuración Centralizada
- ✅ `apps/orchestrator/settings.py` - Pydantic Settings multi-ambiente
- ✅ `apps/orchestrator/databases/postgres.py` - DatabaseManager con pooling
- ✅ Soporte para dev/staging/production

#### 3. Patrones DDD Implementados
- ✅ Entity, AggregateRoot, ValueObject base classes
- ✅ Domain exceptions hierarchy
- ✅ Repository pattern base
- ✅ Unit of Work pattern (estructura preparada)

#### 4. Agentes Modulares (Estructura)
- ✅ `apps/agents/transactional/agent.py` - Factory pattern
- ✅ TransactionalState definido
- ✅ 4 nodos creados (extractor, conversation, validator, transaction)
- ✅ 2 rutas condicionales (intent_route, validation_route)
- ✅ Flujo del grafo definido

#### 5. API Enterprise Base
- ✅ `apps/orchestrator/api/app.py` - Application factory
- ✅ Middlewares: RequestID, Logging, CORS, GZip, TrustedHost
- ✅ Exception handlers centralizados
- ✅ Health checks (/health, /health/ready, /health/live)
- ✅ API v1 router preparado

#### 6. Documentación
- ✅ docs/ARCHITECTURE.md - Arquitectura detallada
- ✅ docs/DEVELOPMENT.md - Este documento
- ✅ README.md profesional con guías de instalación
- ✅ prompts/PROMPTS.md - Estructura preparada
- ✅ notebooks/README.md - Guía de notebooks

---

## 🎯 Próximos Pasos Prioritarios

### Fase 1: Mock API + Routers V1 (SIN AGENTES) - ~8 horas

**Objetivo**: API REST funcional probada con Postman (sin implementar agentes aún)

#### 1. Mock API Externa (1.5h) 🔨

Implementar servicio mock según especificación de prueba técnica.

**Estructura**:
```
mock_api/
├── __init__.py
├── main.py                    # FastAPI app
├── models.py                  # Pydantic models
├── routers/
│   └── transactions.py        # Router con 3 endpoints
└── utils.py                   # Helpers (latencia, fallos)
```

**Endpoints requeridos**:
- `POST /api/v1/transactions/validate` - Valida transacción
- `POST /api/v1/transactions/execute` - Ejecuta transacción
- `GET /api/v1/transactions/{transaction_id}` - Consulta estado

**Comportamiento especial**:
- Latencia aleatoria: 100-500ms
- Fallos aleatorios: 10% de probabilidad
- Estados: `pending` → `completed` (después de 2-5 segundos)

**Ejecución**:
```bash
cd mock_api
uvicorn main:app --reload --port 8001
```

#### 2. Schemas Pydantic (1h) 🔨

Crear schemas para los routers V1.

**Estructura**:
```
apps/orchestrator/v1/schemas/
├── __init__.py
├── chat.py                    # ChatRequest, ChatResponse
├── transaction.py             # Transaction schemas
├── conversation.py            # Conversation schemas
└── common.py                  # BaseResponse, ErrorResponse
```

**Schemas principales**:
```python
# chat.py
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    user_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    transaction_id: str | None = None
    requires_confirmation: bool = False

# transaction.py
class TransactionCreate(BaseModel):
    recipient_phone: str = Field(pattern=r"^\d{10}$")
    amount: float = Field(gt=0)
    currency: str = "COP"
```

#### 3. Routers V1 - Versión Simple (2h) 🔨

Implementar routers sin agente (respuestas hardcodeadas).

**Estructura**:
```
apps/orchestrator/v1/routers/
├── __init__.py
├── chat.py                    # POST /api/v1/chat
├── conversations.py           # GET /api/v1/conversations/{id}
└── transactions.py            # GET /api/v1/transactions/{id}
```

**Beneficios**:
- ✅ Permite probar con Postman inmediatamente
- ✅ No requiere implementar agentes todavía
- ✅ Estructura lista para agregar agente después
- ✅ Se puede validar toda la API REST

#### 4. Cliente HTTP Resiliente (2h) 🔨

Implementar cliente con patrones de resiliencia.

**Ubicación**: `apps/orchestrator/infrastructure/clients/transaction_client.py`

**Patrones obligatorios**:
- Retry Pattern: 3 reintentos con backoff exponencial (1s, 2s, 4s)
- Circuit Breaker: Umbral 5 fallos, timeout 60s
- Timeout: Conexión 5s, lectura 10s
- Logging: Todas las llamadas, reintentos y errores

**Librerías**:
- `tenacity` - Retry pattern
- `pybreaker` - Circuit breaker
- `httpx` - HTTP client async

#### 5. Integración Router + Cliente (1h) 🔨

Conectar el router `/chat` con el `TransactionAPIClient`.

**Flujo básico**:
1. Usuario envía mensaje
2. Router procesa (sin agente, lógica simple)
3. Si detecta intención de transacción → llama a `validate_transaction`
4. Retorna respuesta al usuario

#### 6. Testing con Postman (30min) ✅

Probar todos los endpoints:

**Colección Postman**:
- Mock API - Validate Transaction
- Mock API - Execute Transaction
- Mock API - Get Transaction
- Main API - Chat
- Main API - Health

---

## 🚀 Roadmap Completo

### Fase 2: Database & Persistence (~4 horas)

- [ ] Configurar PostgreSQL con Docker Compose
- [ ] Crear modelos SQLAlchemy 2.0 (async)
- [ ] Implementar migrations con Alembic
- [ ] Implementar repositories (TransactionRepository, ConversationRepository)
- [ ] Tests de persistencia

### Fase 3: Agentes con LLM (~6 horas)

⚠️ **IMPORTANTE**: Usar tokens sabiamente (100,000 tokens límite)

- [ ] Implementar `extractor_node` con LLM (structured output)
- [ ] Implementar `conversation_node` con prompts
- [ ] Implementar `validator_node` con lógica de validación
- [ ] Implementar `transaction_node` con integración externa
- [ ] Configurar checkpointing con PostgresSaver
- [ ] Tests de agente (con mocks de LLM)

**Recomendaciones**:
- Usar `gpt-4o-mini` (económico)
- Limitar historial a 5-10 mensajes
- System prompts concisos (<200 tokens)
- Probar con mocks antes de LLM real

### Fase 4: Integración Completa (~3 horas)

- [ ] Conectar router `/chat` con agente LangGraph
- [ ] Implementar streaming de respuestas (opcional)
- [ ] Manejo de conversaciones con estado
- [ ] Persistir conversaciones y transacciones
- [ ] Tests de integración end-to-end

### Fase 5: DevOps & Docker (~3 horas)

- [ ] Crear Dockerfile multi-stage para API principal
- [ ] Crear Dockerfile para Mock API
- [ ] Docker Compose completo (Postgres, API, Mock)
- [ ] Health checks en containers
- [ ] Scripts de inicialización
- [ ] Testing con `docker-compose up --build`

### Fase 6: Testing & Coverage (~4 horas)

- [ ] Tests unitarios (domain, services, client)
- [ ] Tests de integración (API endpoints)
- [ ] Tests E2E (flujo completo)
- [ ] Alcanzar >70% coverage
- [ ] Coverage report HTML

### Fase 7: Observabilidad (Opcional - ~2 horas)

- [ ] Structured logging con structlog
- [ ] Métricas (opcional: Prometheus)
- [ ] Correlation IDs en todas las requests
- [ ] Error tracking

### Fase 8: CI/CD (Opcional - ~2 horas)

- [ ] GitHub Actions workflow
- [ ] Linting (ruff)
- [ ] Type checking (mypy)
- [ ] Tests automáticos
- [ ] Security scanning (bandit)

---

## 📊 Tabla de Progreso Detallada

| Componente | Estado | Progreso | Prioridad |
|------------|--------|----------|-----------|
| **Estructura Base** | ✅ Completado | 100% | - |
| **Configuración** | ✅ Completado | 100% | - |
| **Shared Layer (DDD)** | ✅ Completado | 100% | - |
| **Agentes Base** | ✅ Completado | 100% | - |
| **API Base** | ✅ Completado | 100% | - |
| **Documentación** | ✅ Completado | 100% | - |
| **Mock API** | ⏸️ Pendiente | 0% | 🔥 Alta |
| **Schemas Pydantic** | ⏸️ Pendiente | 0% | 🔥 Alta |
| **Routers V1** | ⏸️ Pendiente | 0% | 🔥 Alta |
| **Cliente Resiliente** | ⏸️ Pendiente | 0% | 🔥 Alta |
| **Database & ORM** | ⏸️ Pendiente | 0% | 🟡 Media |
| **Agentes con LLM** | ⏸️ Pendiente | 0% | 🟡 Media |
| **Checkpointing** | ⏸️ Pendiente | 0% | 🟡 Media |
| **Testing** | ⏸️ Pendiente | 0% | 🟡 Media |
| **Docker Compose** | ⏸️ Pendiente | 0% | 🟢 Baja |
| **CI/CD** | ⏸️ Pendiente | 0% | 🟢 Baja |

**Progreso Global**: ████████████░░░░░░░░ 60%

---

## 📋 Checklist de Entregables

### Obligatorios (según prueba técnica)

- [ ] **Código Fuente**
  - [ ] Repositorio Git con commits descriptivos
  - [ ] Código limpio con type hints
  - [ ] Estructura organizada

- [ ] **Docker**
  - [ ] Dockerfiles para API y Mock API
  - [ ] docker-compose.yml funcional
  - [ ] .env.example completo
  - [ ] Se ejecuta con `docker-compose up --build`

- [ ] **PROMPTS.md**
  - [ ] Documentación de prompts de desarrollo (Claude)
  - [ ] Documentación de prompts del sistema (OpenAI)
  - [ ] Comparación y decisiones
  - [ ] Optimizaciones de tokens

- [ ] **Base de Datos**
  - [ ] Script SQL de inicialización
  - [ ] Migraciones con Alembic
  - [ ] Tablas: conversations, transactions

- [ ] **Tests**
  - [ ] Tests unitarios
  - [ ] Tests de integración
  - [ ] Cobertura mínima 70%
  - [ ] Coverage report

### Opcionales (Bonus)

- [ ] Observabilidad (logging JSON, métricas, tracing)
- [ ] CI/CD (GitHub Actions, linting, type checking)
- [ ] Diagramas de arquitectura y secuencia
- [ ] Rate limiting
- [ ] Autenticación JWT

---

## 💡 Buenas Prácticas

### Commits

- Usar conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Commits pequeños y frecuentes
- Mensajes descriptivos
- Un commit por feature/fix

### Testing

- Escribir tests antes de implementar (TDD cuando sea posible)
- Mantener coverage >70% desde el inicio
- Usar mocks para LLM en tests
- Tests independientes y reproducibles

### Uso de Tokens OpenAI

⚠️ **IMPORTANTE**: Límite de 100,000 tokens

**Recomendaciones**:
1. Usar modelos mini/nano (consumen ~10x menos tokens)
2. Limitar historial (máximo 5-10 mensajes)
3. System prompts concisos
4. Implementar truncado de contexto
5. Probar con mocks antes de usar LLM real
6. Monitorear uso de tokens

### Desarrollo Incremental

1. Implementar 1 feature → test → commit
2. No intentar todo a la vez
3. Mantener funcionalidad básica funcionando siempre
4. Probar con Postman después de cada implementación

---

## 🎯 Estimaciones de Tiempo

| Fase | Tiempo Estimado | Prioridad |
|------|----------------|-----------|
| Mock API + Routers V1 | 8 horas | 🔥 Alta |
| Database & Persistence | 4 horas | 🟡 Media |
| Agentes con LLM | 6 horas | 🟡 Media |
| Integración Completa | 3 horas | 🟡 Media |
| DevOps & Docker | 3 horas | 🟡 Media |
| Testing & Coverage | 4 horas | 🟡 Media |
| Observabilidad | 2 horas | 🟢 Baja (Bonus) |
| CI/CD | 2 horas | 🟢 Baja (Bonus) |

**Total estimado**: 28-32 horas
**Tiempo recomendado (prueba técnica)**: 8-12 horas

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar documentación en `docs/ARCHITECTURE.md`
2. Consultar especificación en `docs/PRUEBA_TECNICA_AI_AGENT.md`
3. Revisar patrones en `docs/reference/PATRONES_LANGGRAPH.md`

---

**Última actualización**: 2025-01-23
**Versión**: 2.0.0
