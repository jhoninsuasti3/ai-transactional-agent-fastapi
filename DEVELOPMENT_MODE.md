# Modo de Desarrollo Local (Sin Docker Rebuilds)

## Por qué este modo es más rápido

- ✅ Cambios en código reflejados INSTANTÁNEAMENTE (sin rebuild)
- ✅ Hot reload automático con uvicorn y FastAPI
- ✅ Debugging más fácil con logs en terminal
- ✅ Iteración rápida (editar código → guardar → ver resultado)

## Prerequisitos

```bash
# 1. Instalar uv (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependencias del proyecto
uv sync
```

## Arquitectura Actual (SIN servicio "agents" separado)

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   PostgreSQL    │    │   Mock API       │    │ Orchestrator │
│   (Docker)      │    │   (Terminal 1)   │    │ (Terminal 2) │
│   Puerto 5432   │    │   Puerto 8001    │    │ Puerto 8002  │
└─────────────────┘    └──────────────────┘    └──────────────┘
                              │                       │
                              │                       │
                              └───────────────────────┘
                                   LangGraph integrado
                                   (NO hay servicio separado)
```

## Terminal 1: PostgreSQL (Docker - necesario)

PostgreSQL debe correr en Docker porque es una base de datos.

```bash
# Levantar solo PostgreSQL
docker compose up -d postgres

# Verificar que esté corriendo
docker compose ps postgres
```

## Terminal 2: Mock API (Puerto 8001)

```bash
# Navegar al directorio raíz del proyecto
cd /home/jhonmo/apps/retos/ai-transactional-agent-fastapi

# Correr Mock API con uvicorn (hot reload)
uv run uvicorn mock_api.main:app --host 0.0.0.0 --port 8001 --reload

# Verificar: http://localhost:8001/health
```

**Hot reload:** Cualquier cambio en `mock_api/` se refleja automáticamente.

## Terminal 3: Orchestrator (Puerto 8002)

```bash
# Navegar al directorio raíz del proyecto
cd /home/jhonmo/apps/retos/ai-transactional-agent-fastapi

# Correr Orchestrator con uvicorn (hot reload)
uv run uvicorn apps.orchestrator.api.app:app --host 0.0.0.0 --port 8002 --reload

# Verificar: http://localhost:8002/health
```

**Hot reload:** Cualquier cambio en `apps/orchestrator/` o `apps/agents/` se refleja automáticamente.

**IMPORTANTE:** El agente de LangGraph está INTEGRADO en el orchestrator, no hay servicio separado.

## ❌ NO necesitas Terminal 4: LangGraph Dev

**NO uses `langgraph dev`** porque:
- El agente ya está integrado en el orchestrator
- `langgraph dev` es para desarrollar agentes standalone
- Nuestro agente se importa directamente en `apps/orchestrator/v1/routers/chat.py`

## Variables de Entorno Necesarias

Crea un archivo `.env` en la raíz del proyecto (si no existe):

```bash
# Base de datos (PostgreSQL en Docker)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost  # ← Cambiar de "postgres" a "localhost"
POSTGRES_PORT=5432
POSTGRES_DB=transactional_agent

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transactional_agent
LANGGRAPH_CHECKPOINT_DB=postgresql+psycopg://postgres:postgres@localhost:5432/transactional_agent

# Mock API URL (corriendo localmente)
TRANSACTION_SERVICE_URL=http://localhost:8001

# LLM
ANTHROPIC_API_KEY=tu-api-key-aqui
LLM_PROVIDER=anthropic
LLM_MODEL=anthropic:claude-3-5-haiku-20241022

# Opcional: LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
```

## Ejecutar Migraciones de Base de Datos

```bash
# Ejecutar migraciones de Alembic
uv run alembic upgrade head

# Verificar migración actual
uv run alembic current
```

## Workflow de Desarrollo

### Paso 1: Levantar servicios

```bash
# Terminal 1: PostgreSQL
docker compose up -d postgres

# Terminal 2: Mock API
uv run uvicorn apps.mock_api.main:app --port 8001 --reload

# Terminal 3: Orchestrator (con agente integrado)
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload
```

### Paso 2: Hacer cambios en código

Edita cualquier archivo Python en:
- `apps/agents/transactional/` - Agente LangGraph
- `apps/orchestrator/` - API y endpoints
- `apps/mock_api/` - Mock de transacciones

**Los cambios se reflejan automáticamente** sin reiniciar nada.

### Paso 3: Probar endpoints

```bash
# Test health
curl http://localhost:8002/health | jq
curl http://localhost:8001/health | jq

# Test chat simple
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hola","user_id":"user-001"}' | jq

# Test transacción
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Envía $75000 al 3109876543","user_id":"user-002"}' | jq
```

### Paso 4: Ver logs en tiempo real

Los logs aparecen directamente en cada terminal:
- **Terminal 2 (Mock API):** Logs de validaciones y ejecuciones
- **Terminal 3 (Orchestrator):** Logs del agente, nodos, y LLM

## Troubleshooting

### Error: "connection refused" en PostgreSQL

```bash
# Asegúrate que PostgreSQL está corriendo
docker compose ps postgres

# Si no está, levántalo
docker compose up -d postgres
```

### Error: "Address already in use"

```bash
# Ver qué proceso usa el puerto
lsof -i :8001  # o :8002

# Matar el proceso
kill -9 <PID>
```

### Cambios no se reflejan

Verifica que uvicorn esté corriendo con `--reload`:

```bash
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload
#                                                            ^^^^^^^^
```

## Ventajas de este Modo

| Aspecto | Docker | Local con uv |
|---------|--------|--------------|
| Tiempo de rebuild | 20-30s | 0s (hot reload) |
| Ver cambios | Rebuild → restart | Inmediato |
| Debugging | Logs en docker | Logs en terminal |
| Iteración | Lenta | Rápida |

## Cuándo Volver a Docker

Usa Docker cuando:
- ✅ Quieras probar la configuración exacta de producción
- ✅ Vayas a hacer deploy
- ✅ Necesites probar networking entre containers

Para desarrollo diario: **usa modo local**.

---

## Resumen de Comandos

```bash
# Terminal 1: PostgreSQL
docker compose up -d postgres

# Terminal 2: Mock API (está en mock_api/, NO en apps/)
uv run uvicorn mock_api.main:app --port 8001 --reload

# Terminal 3: Orchestrator
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload

# Migraciones (ejecutar una vez)
uv run alembic upgrade head
```

**Ahora puedes editar código y verás cambios INMEDIATAMENTE** 🚀
