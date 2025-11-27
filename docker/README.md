# Docker Infrastructure

This directory contains all Docker-related files for the AI Transactional Agent project.

## Directory Structure

```
docker/
├── dockerfiles/              # Multi-service Dockerfiles
│   ├── Dockerfile.orchestrator   # Main FastAPI orchestrator service
│   ├── Dockerfile.mock_api       # Mock transaction API
│   └── Dockerfile.agents         # LangGraph agents service (future)
└── postgres/                 # PostgreSQL initialization scripts
    └── init.sql             # Database initialization
```

## Services

### 1. **Orchestrator** (`Dockerfile.orchestrator`)
Main FastAPI service that handles:
- API endpoints (chat, transactions, conversations)
- Database persistence with PostgreSQL
- Integration with Mock API via resilient HTTP client
- Auto-migration on startup with Alembic

**Port**: 8000

### 2. **Mock API** (`Dockerfile.mock_api`)
Lightweight service simulating external transaction processor:
- Transaction validation endpoint
- Transaction execution endpoint
- Transaction status queries
- In-memory storage (no database)

**Port**: 8001

### 3. **Agents** (`Dockerfile.agents`)
LangGraph + LangChain agents service (future implementation):
- Conversational AI with state management
- LangGraph workflow orchestration
- Integration with OpenAI API

**Port**: 8002

## Usage

### Build specific service
```bash
docker build -f docker/dockerfiles/Dockerfile.orchestrator -t transactional-agent-orchestrator .
docker build -f docker/dockerfiles/Dockerfile.mock_api -t transactional-agent-mock-api .
docker build -f docker/dockerfiles/Dockerfile.agents -t transactional-agent-agents .
```

### Run with docker-compose (recommended)
```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f orchestrator
docker-compose logs -f mock-api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Multi-stage Build Optimization

All Dockerfiles use multi-stage builds:
1. **Base**: Python 3.12-slim + uv installation
2. **Dependencies**: Install Python dependencies with uv
3. **Production**: Final image with application code

Benefits:
- Smaller final image size
- Faster builds with layer caching
- Separation of build and runtime dependencies

## Health Checks

All services include health checks:
- **Orchestrator**: `GET /health` (40s start period)
- **Mock API**: `GET /health` (10s start period)
- **PostgreSQL**: `pg_isready` command (10s start period)

## Security

- Non-root users in all containers
- No hardcoded credentials (environment variables)
- Read-only volume mounts where possible
- Minimal base images (alpine/slim variants)
