# Agente Conversacional Transaccional - Envíos de Dinero

> Sistema de agente conversacional con IA para procesar envíos de dinero mediante lenguaje natural

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.3-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Coverage->70%25-brightgreen.svg)](docs/PLAN_DE_TRABAJO.md)

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

### Decisiones Arquitectónicas Clave

#### 1. Estructura Enterprise: `apps/` vs `src/`

**Decisión**: Usar `apps/` en lugar de `src/` como convención enterprise para backend Python.

**Justificación**:
- `src/` es común en proyectos frontend (React, Vue, etc.)
- `apps/` es el estándar en proyectos enterprise backend Python (Django, FastAPI grandes)
- Permite escalabilidad futura con múltiples aplicaciones en el mismo monorepo
- Referencia de proyectos profesionales modernos (2025)

```
✅ ESTRUCTURA ENTERPRISE
apps/              # Backend principal
mock_api/          # Sistema externo simulado (separado)
tests/             # Testing
docs/              # Documentación
```

#### 2. Separación Mock API

**Decisión**: Mock API como servicio **standalone y minimalista** separado de `apps/`.

**Justificación**:
- El Mock API simula un **servicio externo de terceros** (ej: PSE, Nequi, Bancolombia)
- En producción real, sería un microservicio independiente o API de terceros
- Mantenerlo simple (90 líneas) enfoca el esfuerzo en la arquitectura principal (`apps/`)
- Comunicación vía HTTP con cliente resiliente (no código compartido)

**Futuro**:
- Mock API se reemplazaría por API real de proveedor de pagos
- `apps/` permanece sin cambios (desacoplamiento total)

#### 3. Arquitectura Hexagonal + DDD

**Decisión**: Implementar Hexagonal Architecture (Ports & Adapters) con Domain-Driven Design.

**Justificación**:
- **Testeable**: Mocking trivial en cada capa
- **Escalable**: Fácil agregar features sin afectar el core
- **Mantenible**: Separación clara de responsabilidades (SOLID)
- **Enterprise-ready**: Estándar en proyectos profesionales Python

**Capas**:
```
apps/
├── core/              # Transversal (config, logging, security)
├── domain/            # Business logic (DDD - independiente de frameworks)
├── application/       # Use cases y orchestration
├── infrastructure/    # Implementaciones concretas (DB, HTTP, etc.)
├── api/              # Capa de presentación (REST API)
└── agent/            # LangGraph (aislado del dominio)
```

### Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Lenguaje** | Python | 3.12+ | Type hints, performance |
| **Framework Web** | FastAPI | 0.121+ | ASGI, async, OpenAPI |
| **Agente** | LangGraph | 1.0.3 | State machines, checkpointing |
| **LLM** | OpenAI | gpt-4.1-mini | Function calling, económico |
| **Base de Datos** | PostgreSQL | 16 | ACID, relacional |
| **ORM** | SQLAlchemy | 2.0.44 | Async, type-safe |
| **Migraciones** | Alembic | 1.17.2 | Versionado de schema |
| **HTTP Client** | httpx | 0.28.1 | Async HTTP/2 |
| **Retry** | tenacity | 9.1.2 | Backoff exponencial |
| **Circuit Breaker** | pybreaker | 1.4.1 | Fault tolerance |
| **Logging** | structlog | 25.5.0 | Structured JSON logs |
| **Testing** | pytest | 8.4.2 | Async, coverage |
| **Linting** | ruff | 0.14.6 | Fast linter |
| **Type Checking** | mypy | 1.18.2 | Strict mode |
| **Package Manager** | uv | 0.9.10 | Ultra-rápido (2025) |

### Estructura del Proyecto

```
📦 ai-transactional-agent-fastapi/
│
├── 📁 apps/                          # 🏢 BACKEND PRINCIPAL (Arquitectura Hexagonal)
│   ├── core/                         # Núcleo transversal
│   │   ├── config.py                 # Pydantic Settings (env vars)
│   │   ├── exceptions.py             # Custom exceptions
│   │   ├── logging.py                # Structured logging (structlog)
│   │   └── security.py               # Auth, JWT (futuro)
│   │
│   ├── domain/                       # 🎯 CAPA DE DOMINIO (DDD)
│   │   ├── models.py                 # Entidades y Value Objects
│   │   ├── ports.py                  # Interfaces/Puertos (Repository, Services)
│   │   └── events.py                 # Domain Events
│   │
│   ├── application/                  # 🔄 CAPA DE APLICACIÓN
│   │   ├── services/                 # Application Services
│   │   ├── use_cases/                # Use Cases (CQRS pattern)
│   │   │   └── send_money_use_case.py
│   │   └── dtos/                     # Data Transfer Objects
│   │
│   ├── infrastructure/               # 🔧 CAPA DE INFRAESTRUCTURA
│   │   ├── persistence/              # SQLAlchemy models, repositories
│   │   │   ├── models.py             # ORM models (conversations, transactions)
│   │   │   └── repositories.py       # Repository implementations
│   │   ├── clients/                  # HTTP clients externos
│   │   │   └── transaction_client.py # Cliente resiliente al Mock API
│   │   └── adapters/                 # Otros adaptadores
│   │
│   ├── api/                          # 🌐 CAPA DE PRESENTACIÓN (REST API)
│   │   ├── v1/                       # API versioning
│   │   │   ├── chat.py               # POST /api/v1/chat
│   │   │   ├── conversations.py      # GET /api/v1/conversations/{id}
│   │   │   └── transactions.py       # GET /api/v1/transactions/{id}
│   │   ├── middleware/               # Custom middlewares
│   │   └── dependencies/             # FastAPI dependencies
│   │
│   ├── agent/                        # 🤖 LANGGRAPH AGENT (Aislado)
│   │   ├── graph/                    # State machine definition
│   │   │   └── transaction_graph.py
│   │   ├── nodes/                    # Graph nodes (extract, validate, confirm, execute)
│   │   ├── state/                    # AgentState (TypedDict)
│   │   ├── tools/                    # LangChain tools (validate_tool, execute_tool)
│   │   └── prompts/                  # System prompts
│   │
│   └── main.py                       # 🚀 FastAPI app entry point
│
├── 📁 mock_api/                      # 🏦 MOCK API EXTERNO (Standalone)
│   ├── __init__.py
│   └── main.py                       # FastAPI simple (90 líneas)
│                                     # Endpoints: /validate, /execute, /{id}
│                                     # Puerto: 8001
│
├── 📁 tests/                         # 🧪 TESTING (>70% coverage)
│   ├── unit/                         # Tests unitarios
│   │   ├── domain/                   # Tests de domain models
│   │   ├── application/              # Tests de use cases
│   │   └── infrastructure/           # Tests de repositories
│   ├── integration/                  # Tests de integración
│   │   ├── agent/                    # Tests del agente LangGraph
│   │   └── api/                      # Tests de endpoints
│   └── e2e/                          # Tests end-to-end
│
├── 📁 alembic/                       # 🗄️ DATABASE MIGRATIONS
│   ├── versions/                     # Migration files
│   └── env.py                        # Alembic config (async)
│
├── 📁 docker/                        # 🐳 DOCKER
│   ├── Dockerfile                    # Multi-stage para apps/
│   ├── Dockerfile.mock               # Para mock_api/
│   └── postgres/
│       └── init.sql                  # PostgreSQL init script
│
├── 📁 docs/                          # 📚 DOCUMENTACIÓN
│   ├── PLAN_DE_TRABAJO.md            # Plan de 5 días
│   ├── ARQUITECTURA.md               # Diagramas, ADRs
│   ├── PATRONES_LANGGRAPH.md         # Patterns LangGraph
│   ├── BITACORA_DESARROLLO.md        # Development log
│   ├── SCOPE_REQUIREMENTS.md         # Checklist
│   └── prompts/
│       └── PROMPTS.md                # 🚨 OBLIGATORIO: Registro de prompts
│
├── 📄 pyproject.toml                 # Project config (uv, pytest, ruff, mypy)
├── 📄 docker-compose.yml             # Orquestación de servicios
├── 📄 .env.example                   # Template de variables
├── 📄 alembic.ini                    # Alembic config
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
│  APPS/ (Backend Principal - Puerto 8000)            │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI)                         │  │
│  │  apps/api/v1/chat.py                         │  │
│  └────────────────┬─────────────────────────────┘  │
│                   │                                 │
│                   ▼                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  LangGraph Agent                             │  │
│  │  apps/agent/graph/transaction_graph.py       │  │
│  │  - State Machine                             │  │
│  │  - Nodes: extract → validate → confirm       │  │
│  └────────────────┬─────────────────────────────┘  │
│                   │                                 │
│                   ▼                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  HTTP Client Resiliente                      │  │
│  │  apps/infrastructure/clients/                │  │
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

---

## 🚀 Quick Start

### Prerrequisitos

- **Python 3.12+**
- **Docker & Docker Compose**
- **Git**
- **API Key de OpenAI** (proporcionada en el correo de la prueba)

### Instalación con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <URL_DEL_REPO>
cd ai-transactional-agent-fastapi

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY

# 3. Levantar servicios con Docker Compose
docker-compose up --build

# Los servicios estarán disponibles en:
# - API Principal:    http://localhost:8000
# - API Docs:         http://localhost:8000/docs
# - Mock API:         http://localhost:8001
# - Mock API Docs:    http://localhost:8001/docs
# - PostgreSQL:       localhost:5432
```

### Instalación Local (Desarrollo)

```bash
# 1. Instalar uv (gestor de paquetes ultra-rápido)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env

# 4. Inicializar base de datos
uv run alembic upgrade head

# 5. Levantar servicios

# Terminal 1: Mock API
uv run python -m mock_api.main

# Terminal 2: API Principal
uv run uvicorn apps.main:app --reload --port 8000
```

---

## 📝 Documentación

### Documentos Principales

1. **[PLAN_DE_TRABAJO.md](docs/PLAN_DE_TRABAJO.md)** - Plan de desarrollo completo (5 días)
2. **[ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Diagramas, patrones, ADRs, decisiones técnicas
3. **[PROMPTS.md](docs/prompts/PROMPTS.md)** - 🚨 **OBLIGATORIO**: Registro de todos los prompts
4. **[PATRONES_LANGGRAPH.md](docs/PATRONES_LANGGRAPH.md)** - Patterns modernos LangGraph
5. **[BITACORA_DESARROLLO.md](docs/BITACORA_DESARROLLO.md)** - Log de desarrollo día a día

### Guía de Arquitectura

El proyecto sigue **Arquitectura Hexagonal (Ports & Adapters)** con **Domain-Driven Design**:

**Principios**:
- ✅ Dominio independiente de frameworks
- ✅ Dependency Inversion (interfaces en domain, implementaciones en infrastructure)
- ✅ Separation of Concerns (cada capa con responsabilidad única)
- ✅ Testeable (mocking trivial con ports)

**Capas** (de adentro hacia afuera):
1. **Domain** (core business): Entidades, Value Objects, Ports
2. **Application** (orchestration): Use Cases, Services, DTOs
3. **Infrastructure** (detalles): DB, HTTP clients, adapters
4. **Presentation** (API): FastAPI endpoints, schemas

**Comunicación entre capas**:
- API → Application (via Use Cases)
- Application → Domain (via Domain Services)
- Application → Infrastructure (via Ports/Interfaces)
- Infrastructure implementa Ports definidos en Domain

**Más detalles**: Ver [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md)

---

## 🧪 Testing

El proyecto tiene >70% de cobertura de tests con pruebas unitarias, de integración y E2E.

```bash
# Ejecutar todos los tests
uv run pytest

# Con coverage
uv run pytest --cov=apps --cov-report=html --cov-report=term

# Ver reporte HTML
open htmlcov/index.html

# Tests específicos
uv run pytest tests/unit/           # Solo unitarios
uv run pytest tests/integration/    # Solo integración
uv run pytest tests/e2e/            # Solo E2E
uv run pytest -m "not slow"         # Excluir tests lentos
```

---

## 🛡️ Patrones de Resiliencia

El sistema implementa patrones de resiliencia industrial en el cliente HTTP:

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
- Contexto completo: request_id, user_id, duration, status
- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Ubicación**: `apps/infrastructure/clients/transaction_client.py`

---

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Linting
uv run ruff check .                 # Check
uv run ruff check . --fix           # Autofix

# Type checking
uv run mypy apps/                   # Strict mode

# Tests
uv run pytest --cov=apps            # Con coverage
uv run pytest -vv                   # Verbose
uv run pytest -x                    # Stop on first failure

# Database
uv run alembic revision --autogenerate -m "description"  # Nueva migración
uv run alembic upgrade head                               # Aplicar
uv run alembic downgrade -1                               # Revertir

# Docker
docker-compose up --build           # Build y run
docker-compose logs -f api          # Logs de API
docker-compose down -v              # Down y limpiar volumes
```

### Variables de Entorno

Ver `.env.example` para la lista completa. Las más importantes:

```bash
# OpenAI
OPENAI_API_KEY=sk-...               # 🚨 OBLIGATORIO
OPENAI_MODEL=gpt-4.1-mini           # Modelo económico

# Database
DATABASE_URL=postgresql+asyncpg://...

# Mock API
MOCK_API_URL=http://mock-api:8001  # En Docker
# MOCK_API_URL=http://localhost:8001  # Local

# Resiliencia
MAX_RETRIES=3
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
```

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~2,000 (sin tests)
- **Líneas de tests**: ~1,500
- **Coverage**: >70% (objetivo)
- **Dependencias**: 107 paquetes
- **Servicios Docker**: 3 (postgres, api, mock-api)
- **Endpoints API**: 5+ (chat, conversations, transactions, health)

---

## 📄 Licencia

Este proyecto es parte de una prueba técnica y es de uso privado.

---

## 👥 Autor

**Desarrollador**: [Tu Nombre]
**Asistente**: Claude Code (Anthropic)
**Fecha**: Enero 2025
**Versión**: 1.0.0

---

**Última actualización**: 2025-01-21