# AI Transactional Agent

> Sistema conversacional con IA para procesar envíos de dinero mediante lenguaje natural

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.27-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-420%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen.svg)](tests/)
[![CI](https://img.shields.io/badge/CI-Passing-success.svg)](.github/workflows/ci.yml)

---

## 🎯 Descripción

Agente conversacional enterprise-ready que permite a usuarios realizar envíos de dinero a través de lenguaje natural. El sistema extrae información clave (número de teléfono y monto), valida con servicios externos, solicita confirmación explícita y ejecuta transacciones de forma segura.

### Ejemplo de Conversación

```
Usuario: "Hola, quiero enviar dinero"
Agente:  "Con gusto. ¿A qué número de celular deseas enviar?"

Usuario: "Al 3001234567"
Agente:  "Perfecto. ¿Qué monto deseas enviar?"

Usuario: "50000 pesos"
Agente:  "Confirmas el envío de $50,000 COP al 3001234567?"

Usuario: "Sí, confirmo"
Agente:  "Transacción completada. ID: TXN-12345"
```

---

## 🚀 Quick Start

### Con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd ai-transactional-agent-fastapi

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y configurar OPENAI_API_KEY

# 3. Levantar todos los servicios
make quick-start
# o: docker compose up -d --build

# 4. Verificar que todo esté corriendo
make health
# o: curl http://localhost:8002/health
```

**Los servicios estarán disponibles en:**
- **Orchestrator API**: http://localhost:8002
- **API Docs (Swagger)**: http://localhost:8002/docs
- **Mock Transaction API**: http://localhost:8001

### Con Makefile

El proyecto incluye un Makefile con comandos útiles:

```bash
# Ver todos los comandos disponibles
make help

# Desarrollo
make quick-start      # Iniciar servicios y verificar salud
make dev             # Full dev reset: clean, build, start, logs
make logs            # Ver logs de todos los servicios
make ps              # Ver estado de servicios

# Testing
make test            # Ejecutar todos los tests
make test-unit       # Solo tests unitarios
make test-integration # Solo tests de integración
make test-cov        # Con reporte de cobertura

# Code Quality
make lint            # Ejecutar ruff linter
make format          # Formatear código con ruff
make type-check      # Type checking con mypy
make pre-commit      # Ejecutar pre-commit hooks

# Database
make db-migrate      # Ejecutar migraciones
make db-shell        # Abrir shell de PostgreSQL
make db-backup       # Backup de base de datos

# Cleanup
make clean           # Limpiar contenedores, volúmenes e imágenes
make down            # Detener servicios
```

---

## 🏗️ Arquitectura

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| **Lenguaje** | Python 3.12+ | Type hints, async/await |
| **Framework Web** | FastAPI 0.115+ | API REST, OpenAPI |
| **Motor de Agentes** | LangGraph 0.2.27 | State machines, grafos de flujo |
| **LLM** | OpenAI GPT-4o-mini | Function calling, bajo costo |
| **Base de Datos** | PostgreSQL 16 | Persistencia ACID |
| **ORM** | SQLAlchemy 2.0+ | Async, type-safe |
| **HTTP Client** | httpx | Async, resiliente |
| **Testing** | pytest | 420 tests, 80% coverage |
| **Package Manager** | uv | Ultra-rápido |

### Componentes del Sistema

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP POST /api/v1/chat
       ▼
┌───────────────────────────────────────────┐
│  Orchestrator (FastAPI + LangGraph)       │
│  Puerto 8002                              │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │  FastAPI API Layer                  │ │
│  │  /api/v1/chat                       │ │
│  └─────────────┬───────────────────────┘ │
│                │                          │
│                ▼                          │
│  ┌─────────────────────────────────────┐ │
│  │  LangGraph Agent (Integrado)        │ │
│  │  • conversation_node                │ │
│  │  • extractor_node                   │ │
│  │  • validator_node                   │ │
│  │  • confirmation_node                │ │
│  │  • transaction_node                 │ │
│  └─────────────┬───────────────────────┘ │
└────────────────┼──────────────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
     ▼                       ▼
┌──────────────┐    ┌──────────────────┐
│  PostgreSQL  │    │  Mock API        │
│  Puerto 5432 │    │  Puerto 8001     │
│              │    │                  │
│ • Checkpoints│    │  • /validate     │
│ • Domain Data│    │  • /execute      │
└──────────────┘    │  • /{id}         │
                    └──────────────────┘
```

**Arquitectura detallada**: Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Estructura del Proyecto

```
📦 ai-transactional-agent-fastapi/
│
├── 📁 apps/                      # Backend principal
│   ├── agents/                   # Agentes LangGraph
│   │   └── transactional/        # Agente transaccional
│   │       ├── agent.py          # Factory del agente
│   │       ├── nodes/            # Nodos del grafo
│   │       ├── state.py          # Estado del agente
│   │       ├── tools/            # Herramientas
│   │       └── prompts/          # System prompts
│   │
│   └── orchestrator/             # Backend FastAPI
│       ├── api/                  # API layer
│       ├── v1/routers/           # Routers v1
│       ├── domain/               # Domain layer (DDD)
│       ├── infrastructure/       # Infrastructure layer
│       ├── services/             # Application services
│       └── core/                 # Config, logging, exceptions
│
├── 📁 mock_api/                  # Mock API externo
├── 📁 tests/                     # Tests (420 tests, 80% coverage)
├── 📁 alembic/                   # Migraciones de DB
├── 📁 docker/                    # Dockerfiles
├── 📁 docs/                      # Documentación completa
│   ├── README.md                 # Índice de documentación
│   ├── ARCHITECTURE.md           # Arquitectura detallada
│   ├── TESTING.md                # Guía de testing
│   ├── DOCKER.md                 # Guía de Docker
│   ├── DEVELOPMENT.md            # Guía de desarrollo
│   ├── CODE_QUALITY.md           # Estándares de código
│   └── CI_CD.md                  # Pipeline CI/CD
│
├── 📄 Makefile                   # Comandos de desarrollo
├── 📄 pyproject.toml             # Configuración del proyecto
├── 📄 docker-compose.yml         # Orquestación de servicios
└── 📄 .env.example               # Template de variables
```

---

## 📖 Uso de la API

### Endpoint Principal: Chat

```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quiero enviar 50000 pesos al 3001234567",
    "user_id": "user-123"
  }'
```

**Respuesta:**
```json
{
  "response": "Confirmas el envío de $50,000 COP al 3001234567?",
  "conversation_id": "conv-abc123",
  "transaction_id": null,
  "requires_confirmation": true,
  "metadata": {
    "phone": "3001234567",
    "amount": 50000
  }
}
```

### Flujo Completo

```bash
# 1. Inicio de conversación
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "user_id": "user-123"}'

# 2. Proporcionar datos (todo en un mensaje)
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Enviar 50000 al 3001234567",
    "user_id": "user-123",
    "conversation_id": "<id_del_paso_1>"
  }'

# 3. Confirmar transacción
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sí, confirmo",
    "user_id": "user-123",
    "conversation_id": "<id>"
  }'
```

### Otros Endpoints

```bash
# Health Check
curl http://localhost:8002/health

# Documentación interactiva
open http://localhost:8002/docs

# Consultar conversación
curl http://localhost:8002/api/v1/conversations/{conversation_id}

# Consultar transacción
curl http://localhost:8002/api/v1/transactions/{transaction_id}
```

---

## 🧪 Testing

El proyecto mantiene **80% de cobertura** con **420 tests** (verificado en CI).

```bash
# Ejecutar todos los tests
make test

# Con cobertura detallada
make test-cov

# Solo tests unitarios
make test-unit

# Solo tests de integración
make test-integration

# Tests específicos
make test-specific TEST=tests/unit/agents/nodes/test_conversation_node.py
```

**Guía completa**: Ver [docs/TESTING.md](docs/TESTING.md)

---

## 🛡️ Patrones de Resiliencia

El sistema implementa patrones enterprise:

- **Retry Pattern**: Máximo 3 reintentos con backoff exponencial (1s → 2s → 4s)
- **Circuit Breaker**: Se abre tras 5 fallos consecutivos, timeout de 60s
- **Timeout Pattern**: Conexión 5s, Lectura 10s, Total 15s max
- **Structured Logging**: Logs JSON con contexto completo

**Ubicación**: `apps/orchestrator/infrastructure/clients/`

---

## 🔧 Desarrollo Local

### Instalación Local (Sin Docker)

```bash
# 1. Instalar uv (gestor de paquetes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar e instalar dependencias
git clone <URL>
cd ai-transactional-agent-fastapi
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con OPENAI_API_KEY

# 4. Inicializar base de datos
# Con PostgreSQL local:
createdb transactional_agent
uv run alembic upgrade head

# Con Docker solo PostgreSQL:
docker compose up -d postgres
uv run alembic upgrade head

# 5. Levantar servicios (2 terminales)
# Terminal 1: Mock API
uv run uvicorn mock_api.main:app --port 8001 --reload

# Terminal 2: Orchestrator
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload
```

### Calidad de Código

```bash
# Instalar pre-commit hooks
make install-hooks

# Ejecutar checks manualmente
make lint          # Ruff linter
make format        # Ruff formatter
make type-check    # MyPy type checking
make pre-commit    # Todos los hooks
```

### Variables de Entorno Requeridas

```bash
# Mínimo requerido en .env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transactional_agent
LANGGRAPH_CHECKPOINT_DB=postgresql+psycopg://postgres:postgres@localhost:5432/transactional_agent
TRANSACTION_SERVICE_URL=http://localhost:8001
```

**Configuración completa**: Ver `.env.example`

---

## 📚 Documentación

### Guías Principales

Toda la documentación está organizada en [`docs/`](docs/):

- **[docs/README.md](docs/README.md)** - Índice completo de documentación
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura del sistema
- **[docs/TESTING.md](docs/TESTING.md)** - Guía de testing completa
- **[docs/DOCKER.md](docs/DOCKER.md)** - Setup y operaciones Docker
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Guía de desarrollo
- **[docs/CODE_QUALITY.md](docs/CODE_QUALITY.md)** - Estándares de código
- **[docs/CI_CD.md](docs/CI_CD.md)** - Pipeline CI/CD

### Por Caso de Uso

- **"Quiero correr el proyecto"** → [docs/DOCKER.md](docs/DOCKER.md)
- **"Quiero entender la arquitectura"** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **"Quiero ejecutar tests"** → [docs/TESTING.md](docs/TESTING.md)
- **"Quiero contribuir"** → [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md)

---

## 🐛 Troubleshooting

### Problemas Comunes

**1. Error de conexión a PostgreSQL**
```bash
docker compose ps postgres          # Verificar que esté corriendo
docker compose logs postgres        # Ver logs
docker compose restart postgres     # Reiniciar
```

**2. Error de OpenAI API Key**
```bash
cat .env | grep OPENAI_API_KEY      # Verificar configuración
```

**3. Puerto ya en uso**
```bash
# Cambiar puerto en .env
API_PORT=8003  # O cualquier otro disponible
```

**4. Tests fallando**
```bash
make clean-test                     # Limpiar artifacts
uv sync                             # Reinstalar dependencias
make test                           # Ejecutar tests
```

**Más troubleshooting**: Ver [docs/DOCKER.md](docs/DOCKER.md#troubleshooting)

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~3,500 (sin tests)
- **Test Coverage**: 80% (420 tests)
  - Tests unitarios: 385
  - Tests de integración: 35
- **CI/CD**: Pipeline completamente funcional
- **Endpoints API**: 6+
- **Servicios Docker**: 3 (postgres, orchestrator, mock-api)
- **Dependencias**: 50+ paquetes (gestionadas con uv)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Instalar pre-commit: `make install-hooks`
4. Commit cambios (`git commit -m 'feat: nueva funcionalidad'`)
5. Push a la rama (`git push origin feature/nueva-funcionalidad`)
6. Abrir Pull Request

**Estándares de código**: Ver [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md)

---

## 📄 Licencia

Este proyecto es parte de una prueba técnica y es de uso privado.

---

**Versión**: 1.0.0
**Python**: 3.12+
**Última actualización**: 2025-01-27
