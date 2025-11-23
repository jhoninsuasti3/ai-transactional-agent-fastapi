# Agente Conversacional Transaccional - Envíos de Dinero

> Sistema de agente conversacional con IA para procesar envíos de dinero mediante lenguaje natural

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://python.langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.27-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

---

## 🎯 Descripción

Agente conversacional transaccional enterprise-ready que permite a usuarios realizar envíos de dinero
a través de lenguaje natural. El sistema extrae información clave (número de teléfono y monto),
valida con servicios externos, solicita confirmación explícita y ejecuta la transacción de forma segura.

### Ejemplo de Conversación

```
Usuario: "Hola, quiero enviar dinero"
Agente:  "Con gusto te ayudo. ¿A qué número de celular deseas enviar el dinero?"

Usuario: "Al 3001234567"
Agente:  "Perfecto, 3001234567. ¿Qué monto deseas enviar?"

Usuario: "50000 pesos"
Agente:  "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?"

Usuario: "Sí, confirmo"
Agente:  "Transacción completada exitosamente. El ID de tu transacción es: TXN-12345"
```

---

## 🏗️ Arquitectura

### Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Lenguaje** | Python | 3.12+ | Type hints, performance |
| **Framework Web** | FastAPI | 0.115+ | ASGI, async, OpenAPI |
| **Motor de Agentes** | LangChain | 0.3+ | Framework base para agentes AI |
| **Orquestación** | LangGraph | 0.2.27 | State machines, checkpointing, flujos |
| **LLM** | OpenAI | gpt-4o-mini | Function calling, económico |
| **Base de Datos** | PostgreSQL | 16 | ACID, relacional |
| **ORM** | SQLAlchemy | 2.0+ | Async, type-safe |
| **Migraciones** | Alembic | 1.13+ | Versionado de schema |
| **HTTP Client** | httpx | 0.27+ | Async HTTP/2 |
| **Retry** | tenacity | 9.0+ | Backoff exponencial |
| **Circuit Breaker** | pybreaker | 1.2+ | Fault tolerance |
| **Logging** | structlog | 24.4+ | Structured JSON logs |
| **Testing** | pytest | 8.3+ | Async, coverage |
| **Linting** | ruff | 0.6+ | Fast linter |
| **Type Checking** | mypy | 1.11+ | Strict mode |
| **Package Manager** | uv | Latest | Ultra-rápido |

### Estructura del Proyecto

```
📦 ai-transactional-agent-fastapi/
│
├── 📁 apps/                          # Backend principal (Arquitectura Enterprise)
│   ├── agents/                       # Agentes LangGraph
│   │   ├── shared/                   # Componentes compartidos entre agentes
│   │   └── transactional/            # Agente transaccional
│   │       ├── agent.py              # Factory del agente
│   │       ├── nodes/                # Nodos del grafo (extract, validate, confirm)
│   │       ├── state/                # Estado del agente (TypedDict)
│   │       └── tools/                # Herramientas LangChain
│   │
│   └── orchestrator/                 # Backend y orquestación
│       ├── api/                      # Endpoints FastAPI
│       │   ├── app.py                # Aplicación principal
│       │   ├── middlewares/          # Custom middlewares
│       │   └── exception_handlers/   # Manejadores de excepciones
│       │
│       ├── v1/                       # API v1
│       │   ├── routers/              # Routers de FastAPI
│       │   │   ├── chat.py           # POST /api/v1/chat
│       │   │   ├── conversations.py  # GET /api/v1/conversations/{id}
│       │   │   └── health.py         # GET /api/v1/health
│       │   └── schemas/              # Pydantic schemas
│       │
│       ├── domain/                   # Capa de dominio (DDD)
│       │   ├── entities/             # Entidades de negocio
│       │   ├── value_objects/        # Value Objects
│       │   └── exceptions/           # Excepciones de dominio
│       │
│       ├── infrastructure/           # Infraestructura
│       │   ├── clients/              # Clientes HTTP resilientes
│       │   ├── database/             # Configuración de DB
│       │   └── repositories/         # Implementación de repositorios
│       │
│       ├── services/                 # Servicios de aplicación
│       ├── utils/                    # Utilidades
│       ├── formatters/               # Formateadores de datos
│       ├── validators/               # Validadores de negocio
│       └── settings.py               # Configuración centralizada (Pydantic)
│
├── 📁 mock_api/                      # Mock API externo (standalone)
│   └── main.py                       # FastAPI simple (puerto 8001)
│
├── 📁 tests/                         # Testing (>70% coverage)
│   ├── unit/                         # Tests unitarios
│   ├── integration/                  # Tests de integración
│   └── e2e/                          # Tests end-to-end
│
├── 📁 alembic/                       # Migraciones de base de datos
│   └── versions/                     # Archivos de migración
│
├── 📁 docker/                        # Configuración Docker
│   ├── Dockerfile                    # Imagen principal
│   └── Dockerfile.mock               # Imagen mock API
│
├── 📁 docs/                          # Documentación del proyecto
│   ├── ARCHITECTURE_ENTERPRISE.md    # Arquitectura detallada
│   ├── MIGRATION_GUIDE.md            # Guía de migración
│
├── 📁 prompts/                       # Templates de prompts
│   └── PROMPTS.md                    # Registro de prompts
│
├── 📁 notebooks/                     # Jupyter notebooks (experimentos)
│
├── 📄 pyproject.toml                 # Configuración del proyecto (uv)
├── 📄 docker-compose.yml             # Orquestación de servicios
├── 📄 .env.example                   # Template de variables de entorno
├── 📄 alembic.ini                    # Configuración de Alembic
├── 📄 main.py                        # Entry point de la aplicación
└── 📄 README.md                      # Este archivo
```

### Flujo de Comunicación

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP POST /api/v1/chat
       ▼
┌─────────────────────────────────────────────────────┐
│  APPS/ORCHESTRATOR (Backend - Puerto 8000)         │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI)                         │  │
│  │  apps/orchestrator/v1/routers/chat.py        │  │
│  └────────────────┬─────────────────────────────┘  │
│                   │                                 │
│                   ▼                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  LangGraph Agent                             │  │
│  │  apps/agents/transactional/agent.py          │  │
│  │  - State Machine                             │  │
│  │  - Nodes: extract → validate → confirm       │  │
│  └────────────────┬─────────────────────────────┘  │
│                   │                                 │
│                   ▼                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  HTTP Client Resiliente                      │  │
│  │  apps/orchestrator/infrastructure/clients/   │  │
│  │  - Retry (tenacity)                          │  │
│  │  - Circuit Breaker (pybreaker)               │  │
│  │  - Timeout (httpx)                           │  │
│  └────────────────┬─────────────────────────────┘  │
└───────────────────┼──────────────────────────────────┘
                    │ HTTP Request
                    ▼
           ┌────────────────────────┐
           │  MOCK_API/             │
           │  (Puerto 8001)         │
           │  - /validate           │
           │  - /execute            │
           │  - /{id}               │
           └────────────────────────┘
```

### Arquitectura Enterprise

El proyecto implementa **Arquitectura Hexagonal (Ports & Adapters)** con **Domain-Driven Design**:

**Principios clave**:
- ✅ Dominio independiente de frameworks
- ✅ Dependency Inversion (interfaces en domain, implementaciones en infrastructure)
- ✅ Separation of Concerns (cada capa con responsabilidad única)
- ✅ Testeable (mocking trivial con ports)
- ✅ Escalable (fácil agregar features sin afectar el core)

**Capas** (de adentro hacia afuera):
1. **Domain** (core business): Entidades, Value Objects, Excepciones
2. **Application** (orchestration): Services, Use Cases
3. **Infrastructure** (detalles): DB, HTTP clients, repositories
4. **Presentation** (API): FastAPI endpoints, schemas

**Más detalles**: Ver [docs/ARCHITECTURE_ENTERPRISE.md](docs/ARCHITECTURE_ENTERPRISE.md)

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.12+**
- **Docker & Docker Compose** (recomendado)
- **Git**
- **API Key de OpenAI**

### Opción 1: Docker Compose (Recomendado)

La forma más rápida de levantar el proyecto completo:

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd ai-transactional-agent-fastapi

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Editar .env y configurar las variables necesarias
# Mínimo requerido:
#   - OPENAI_API_KEY=sk-...
#   - DATABASE_URL (ya configurado para Docker)
nano .env  # o tu editor preferido

# 4. Levantar todos los servicios
docker-compose up --build

# 5. Los servicios estarán disponibles en:
# - API Principal:    http://localhost:8000
# - API Docs:         http://localhost:8000/docs
# - Mock API:         http://localhost:8001
# - Mock API Docs:    http://localhost:8001/docs
# - PostgreSQL:       localhost:5432
```

### Opción 2: Instalación Local (Desarrollo)

Para desarrollo local con hot-reload:

#### Paso 1: Instalar UV (Gestor de Paquetes)

```bash
# Linux/MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verificar instalación
uv --version
```

#### Paso 2: Configurar el Proyecto

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd ai-transactional-agent-fastapi

# 2. Instalar dependencias (incluyendo dev)
uv sync

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Editar .env con tus configuraciones
nano .env
```

#### Paso 3: Configurar Variables de Entorno

Edita `.env` con las siguientes configuraciones mínimas:

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURACIÓN OBLIGATORIA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# OpenAI API Key (OBLIGATORIO)
OPENAI_API_KEY=sk-...

# Base de datos PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transactional_agent

# Mock API URL
MOCK_API_URL=http://localhost:8001

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURACIÓN OPCIONAL (con valores por defecto)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Entorno
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# OpenAI Model
OPENAI_MODEL=gpt-4o-mini

# Resiliencia
MAX_RETRIES=3
RETRY_DELAY=1
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
HTTP_TIMEOUT=15
```

#### Paso 4: Inicializar Base de Datos

```bash
# Opción A: Usar PostgreSQL local
# Asegúrate de tener PostgreSQL 16+ instalado y corriendo
# Crear la base de datos:
createdb transactional_agent

# Ejecutar migraciones
uv run alembic upgrade head

# Opción B: Usar PostgreSQL con Docker
docker run -d \
  --name postgres-transactional \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=transactional_agent \
  -p 5432:5432 \
  postgres:16-alpine

# Ejecutar migraciones
uv run alembic upgrade head
```

#### Paso 5: Levantar los Servicios

Necesitas 2 terminales:

```bash
# Terminal 1: Mock API
uv run python -m mock_api.main
# Mock API corriendo en http://localhost:8001

# Terminal 2: API Principal
uv run python main.py
# API Principal corriendo en http://localhost:8000
```

### Verificar Instalación

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health

# 2. Documentación interactiva
# Abrir en navegador: http://localhost:8000/docs

# 3. Ejecutar tests
uv run pytest

# 4. Ver coverage
uv run pytest --cov=apps --cov-report=html
open htmlcov/index.html  # MacOS
# o xdg-open htmlcov/index.html  # Linux
```

---

## 📖 Uso de la API

### Endpoint Principal: Chat

```bash
# POST /api/v1/chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quiero enviar 50000 pesos al 3001234567",
    "conversation_id": "conv-123",
    "user_id": "user-456"
  }'

# Respuesta
{
  "response": "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?",
  "conversation_id": "conv-123",
  "state": "awaiting_confirmation"
}
```

### Flujo Completo de Conversación

```bash
# 1. Inicio de conversación
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "user_id": "user-123"}'

# 2. Proporcionar número de teléfono
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Al 3001234567",
    "conversation_id": "<conversation_id_del_paso_1>",
    "user_id": "user-123"
  }'

# 3. Proporcionar monto
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "50000 pesos",
    "conversation_id": "<conversation_id>",
    "user_id": "user-123"
  }'

# 4. Confirmar transacción
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sí, confirmo",
    "conversation_id": "<conversation_id>",
    "user_id": "user-123"
  }'
```

### Otros Endpoints

```bash
# Health Check
curl http://localhost:8000/api/v1/health

# Consultar conversación
curl http://localhost:8000/api/v1/conversations/{conversation_id}

# Consultar transacción
curl http://localhost:8000/api/v1/transactions/{transaction_id}
```

---

## 🧪 Testing

El proyecto mantiene >70% de cobertura con tests unitarios, de integración y E2E.

```bash
# Ejecutar todos los tests
uv run pytest

# Con coverage y reporte detallado
uv run pytest --cov=apps --cov-report=html --cov-report=term-missing

# Ver reporte HTML
open htmlcov/index.html  # MacOS
xdg-open htmlcov/index.html  # Linux

# Tests específicos
uv run pytest tests/unit/              # Solo unitarios
uv run pytest tests/integration/       # Solo integración
uv run pytest tests/e2e/                # Solo E2E

# Tests por marcador
uv run pytest -m "not slow"             # Excluir tests lentos
uv run pytest -m unit                   # Solo tests unitarios

# Ejecutar un test específico
uv run pytest tests/unit/test_agent.py::test_extract_node -v

# Con logs
uv run pytest -v --log-cli-level=INFO

# Stop on first failure
uv run pytest -x

# Parallel execution (más rápido)
uv run pytest -n auto
```

---

## 🛡️ Patrones de Resiliencia

El sistema implementa patrones de resiliencia industrial:

### 1. Retry Pattern (tenacity)
- **Reintentos**: Máximo 3
- **Backoff**: Exponencial (1s → 2s → 4s)
- **Errores retry-ables**: Timeout, ConnectionError, 503, 504
- **Logging**: Cada reintento se registra

### 2. Circuit Breaker (pybreaker)
- **Umbral de fallos**: 5 fallos consecutivos → OPEN
- **Timeout en OPEN**: 60 segundos
- **Half-Open**: Permite 1 request de prueba después de timeout
- **Estados**: CLOSED (normal) → OPEN (bloqueado) → HALF_OPEN (test) → CLOSED

### 3. Timeout Pattern (httpx)
- **Conexión**: 5 segundos
- **Lectura**: 10 segundos
- **Total**: 15 segundos máximo por request

### 4. Structured Logging (structlog)
- Logs en formato JSON
- Contexto completo: request_id, conversation_id, duration, status
- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Ubicación**: `apps/orchestrator/infrastructure/clients/`

---

## 🔧 Desarrollo

### Comandos Útiles

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LINTING Y FORMATEO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Linting con Ruff
uv run ruff check .                    # Check
uv run ruff check . --fix              # Autofix
uv run ruff format .                   # Format

# Type checking con mypy
uv run mypy apps/                      # Strict mode

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Crear nueva migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Revertir última migración
uv run alembic downgrade -1

# Ver historial de migraciones
uv run alembic history

# Ver SQL de migración sin aplicar
uv run alembic upgrade head --sql

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOCKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Build y levantar servicios
docker-compose up --build

# Levantar en background
docker-compose up -d

# Ver logs
docker-compose logs -f                 # Todos los servicios
docker-compose logs -f api             # Solo API principal
docker-compose logs -f mock-api        # Solo Mock API

# Reiniciar un servicio
docker-compose restart api

# Detener servicios
docker-compose down

# Detener y limpiar volumes
docker-compose down -v

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEPENDENCIAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Agregar dependencia
uv add <paquete>

# Agregar dependencia de desarrollo
uv add --dev <paquete>

# Actualizar dependencias
uv sync

# Listar dependencias
uv pip list
```

### Pre-commit Hooks (Opcional)

```bash
# Instalar pre-commit
uv run pre-commit install

# Ejecutar manualmente
uv run pre-commit run --all-files
```

### Variables de Entorno Completas

Ver `.env.example` para la lista completa de variables configurables:

```bash
# Application
ENVIRONMENT=development|staging|production
APP_NAME=AI Transactional Agent

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# OpenAI
OPENAI_API_KEY=sk-...                 # OBLIGATORIO
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
OPENAI_MAX_TOKENS=500

# Mock API
MOCK_API_URL=http://localhost:8001

# Resiliencia
MAX_RETRIES=3
RETRY_DELAY=1
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
HTTP_TIMEOUT=15
HTTP_CONNECT_TIMEOUT=5
HTTP_READ_TIMEOUT=10
```

---

## 📚 Documentación Adicional

### Documentos Principales

- **[ARCHITECTURE_ENTERPRISE.md](docs/ARCHITECTURE_ENTERPRISE.md)** - Arquitectura detallada del proyecto
- **[MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - Guía de migración a arquitectura enterprise
- **[STATUS_ENTERPRISE.md](docs/STATUS_ENTERPRISE.md)** - Estado actual y roadmap
- **[COMMITS_GUIDE.md](docs/COMMITS_GUIDE.md)** - Guía de commits incrementales
- **[PATRONES_LANGGRAPH.md](docs/PATRONES_LANGGRAPH.md)** - Patrones modernos de LangGraph
- **[TESTING_INSTRUCTIONS.md](docs/TESTING_INSTRUCTIONS.md)** - Estrategia de testing

### Guías Rápidas

- **[prompts/PROMPTS.md](prompts/PROMPTS.md)** - Registro de prompts del sistema
- **[notebooks/README.md](notebooks/README.md)** - Guía de uso de notebooks

---

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

#### 2. Error de OpenAI API Key

```bash
# Verificar que la variable esté configurada
echo $OPENAI_API_KEY

# O en .env
cat .env | grep OPENAI_API_KEY
```

#### 3. Error al ejecutar migraciones

```bash
# Verificar conexión a DB
uv run alembic current

# Reset de migraciones (CUIDADO: borra datos)
uv run alembic downgrade base
uv run alembic upgrade head
```

#### 4. Tests fallando

```bash
# Limpiar cache de pytest
uv run pytest --cache-clear

# Reinstalar dependencias
rm -rf .venv
uv sync
```

#### 5. Puerto ya en uso

```bash
# Cambiar puerto en .env
API_PORT=8001  # O cualquier otro puerto disponible

# O matar el proceso que usa el puerto
lsof -ti:8000 | xargs kill -9  # MacOS/Linux
```

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~3,000 (sin tests)
- **Líneas de tests**: ~2,000
- **Coverage**: >70%
- **Dependencias**: 50+ paquetes
- **Servicios Docker**: 3 (postgres, api, mock-api)
- **Endpoints API**: 5+

---

## 📄 Licencia

Este proyecto es parte de una prueba técnica y es de uso privado.

---

## 👤 Información del Proyecto

**Versión**: 1.0.0
**Python**: 3.12+
**Framework**: FastAPI 0.115+
**IA**: LangGraph 0.2.27

---

**Última actualización**: 2025-01-23