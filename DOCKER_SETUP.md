# 🐳 Docker Setup Guide

Guía completa para ejecutar el proyecto AI Transactional Agent con Docker desde cero.

## 📋 Prerrequisitos

- Docker Engine 20.10+ instalado
- Docker Compose v2+ instalado
- Al menos 2GB de RAM disponible
- Puertos libres: 5432 (PostgreSQL), 8001 (Mock API), 8002 (Orchestrator)

Verificar instalación:
```bash
docker --version
docker compose version
```

## 🚀 Quick Start (Desde Cero)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd ai-transactional-agent-fastapi
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

Edita `.env` y configura las siguientes variables críticas:
```bash
# OBLIGATORIO: Agregar tu API key de OpenAI
OPENAI_API_KEY=sk-your-actual-api-key-here

# Opcional: Cambiar en producción
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Build y levantar servicios
```bash
# Build y levantar en background
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f
```

### 4. Verificar que todos los servicios estén saludables
```bash
# Ver estado de servicios
docker compose ps

# Verificar health endpoints
curl http://localhost:8001/health  # Mock API - debe retornar 200
curl http://localhost:8002/health  # Orchestrator - debe retornar 200
```

### 5. Probar el agente
```bash
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "Quiero enviar $50000 al número 3001234567"
  }'
```

## 🏗️ Arquitectura de Servicios

El proyecto incluye los siguientes servicios Docker:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **postgres** | 5432 | PostgreSQL 16 - Base de datos principal con checkpointing de LangGraph |
| **mock-api** | 8001 | Mock Transaction API - Simula servicio externo de transacciones |
| **orchestrator** | 8002 | FastAPI + LangGraph Agent - Servicio principal con agente conversacional |

### Dependencias entre servicios

```
orchestrator
├── postgres (base de datos + LangGraph checkpoints)
└── mock-api (servicio de transacciones)
```

## 🔧 Comandos Útiles

### Gestión de servicios

```bash
# Levantar servicios
docker compose up -d

# Detener servicios (mantiene volúmenes)
docker compose stop

# Reiniciar un servicio específico
docker compose restart orchestrator

# Ver logs de un servicio
docker compose logs -f orchestrator

# Ver logs de todos los servicios
docker compose logs -f
```

### Limpieza completa

```bash
# Detener y eliminar contenedores, volúmenes y redes
docker compose down -v

# Eliminar imágenes del proyecto
docker compose down --rmi all

# Limpiar todo el sistema Docker (CUIDADO: afecta otros proyectos)
docker system prune -a --volumes
```

### Rebuilding

```bash
# Rebuild sin cache de un servicio específico
docker compose build --no-cache orchestrator

# Rebuild todo desde cero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 🧪 Ejecutar Tests

### Tests unitarios

```bash
# Ejecutar todos los tests
docker compose exec orchestrator pytest -v

# Ejecutar con cobertura
docker compose exec orchestrator pytest --cov=apps --cov-report=term-missing --cov-report=html

# Ver reporte de cobertura HTML
docker compose exec orchestrator cat htmlcov/index.html
```

### Tests de integración

```bash
# Solo tests de integración
docker compose exec orchestrator pytest tests/integration/ -v

# Test específico
docker compose exec orchestrator pytest tests/integration/test_chat_integration.py -v
```

### Tests con logs detallados

```bash
# Con output de prints
docker compose exec orchestrator pytest -v -s

# Con logs de nivel DEBUG
docker compose exec orchestrator pytest -v --log-cli-level=DEBUG
```

## 🔍 Debug y Troubleshooting

### Ver logs de base de datos

```bash
# Logs de PostgreSQL
docker compose logs -f postgres

# Conectarse a PostgreSQL
docker compose exec postgres psql -U postgres -d transactional_agent

# Ver tablas
docker compose exec postgres psql -U postgres -d transactional_agent -c "\dt"

# Ver conversaciones
docker compose exec postgres psql -U postgres -d transactional_agent -c "SELECT * FROM conversations LIMIT 10;"

# Ver transacciones
docker compose exec postgres psql -U postgres -d transactional_agent -c "SELECT * FROM transactions LIMIT 10;"
```

### Verificar salud de servicios

```bash
# Ver estado detallado
docker compose ps

# Inspeccionar un contenedor
docker inspect transactional-agent-orchestrator

# Ver recursos utilizados
docker stats
```

### Rebuild por problemas de dependencias

```bash
# Si hay problemas con dependencias Python
docker compose down
docker compose build --no-cache orchestrator
docker compose up -d
```

### Acceder al shell de un contenedor

```bash
# Shell en orchestrator
docker compose exec orchestrator /bin/bash

# Shell en postgres
docker compose exec postgres /bin/bash

# Shell en mock-api
docker compose exec mock-api /bin/bash
```

## 🗃️ Gestión de Base de Datos

### Migraciones con Alembic

```bash
# Crear nueva migración
docker compose exec orchestrator alembic revision --autogenerate -m "description"

# Aplicar migraciones
docker compose exec orchestrator alembic upgrade head

# Ver historial de migraciones
docker compose exec orchestrator alembic history

# Rollback a versión anterior
docker compose exec orchestrator alembic downgrade -1
```

### Backup y restore

```bash
# Backup de la base de datos
docker compose exec postgres pg_dump -U postgres transactional_agent > backup.sql

# Restore desde backup
docker compose exec -T postgres psql -U postgres transactional_agent < backup.sql

# Backup de volúmenes
docker run --rm -v transactional-agent-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## 📊 Monitoreo

### Ver logs estructurados (JSON)

```bash
# Logs del orchestrator en formato JSON
docker compose logs orchestrator | jq .

# Filtrar logs por nivel
docker compose logs orchestrator | jq 'select(.level=="ERROR")'

# Logs de transacciones
docker compose logs orchestrator | jq 'select(.event=="transaction_executed")'
```

### Métricas de recursos

```bash
# Ver uso de recursos en tiempo real
docker stats

# Ver tamaño de volúmenes
docker volume ls
docker system df -v
```

## 🌐 Probar Endpoints

### Health checks

```bash
# Orchestrator health
curl http://localhost:8002/health

# Readiness check
curl http://localhost:8002/health/ready

# Liveness check
curl http://localhost:8002/health/live
```

### Chat endpoints

```bash
# Enviar mensaje inicial
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "Hola, quiero enviar dinero"
  }'

# Enviar transacción completa
curl -X POST http://localhost:8002/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "Envía 50000 pesos al 3001234567"
  }'

# Ver conversación
curl http://localhost:8002/api/v1/conversations/{conversation_id}
```

### Mock API

```bash
# Health check
curl http://localhost:8001/health

# Validar transacción
curl -X POST http://localhost:8001/api/transactions/validate \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "3001234567",
    "amount": 50000
  }'

# Ejecutar transacción
curl -X POST http://localhost:8001/api/transactions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "3001234567",
    "amount": 50000,
    "validation_id": "val_123"
  }'

# Consultar estado de transacción
curl http://localhost:8001/api/transactions/{transaction_id}/status
```

## 🐛 Problemas Comunes

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
lsof -i :8002
sudo netstat -tulpn | grep :8002

# Cambiar puerto en docker-compose.yml
ports:
  - "8003:8002"  # Usar 8003 en lugar de 8002
```

### Migraciones no se aplican

```bash
# Aplicar migraciones manualmente
docker compose exec orchestrator alembic upgrade head

# Si falla, verificar conexión a DB
docker compose exec orchestrator python -c "from apps.orchestrator.infrastructure.persistence.database import engine; print(engine)"
```

### Contenedor se reinicia constantemente

```bash
# Ver por qué falla
docker compose logs orchestrator --tail=50

# Ver exit code
docker inspect transactional-agent-orchestrator | jq '.[0].State'

# Ejecutar health check manualmente
docker compose exec orchestrator curl -f http://localhost:8002/health
```

### Problemas de memoria

```bash
# Ver uso de memoria
docker stats

# Aumentar límites en docker-compose.yml
services:
  orchestrator:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Error de conexión a PostgreSQL

```bash
# Verificar que postgres esté corriendo
docker compose ps postgres

# Ver logs de postgres
docker compose logs postgres

# Probar conexión manualmente
docker compose exec postgres psql -U postgres -d transactional_agent -c "SELECT 1;"
```

## 📝 Buenas Prácticas

1. **Siempre usar volúmenes nombrados** para datos persistentes
2. **Definir health checks** en todos los servicios
3. **Usar networks personalizadas** para aislamiento
4. **Configurar restart policies** adecuadamente
5. **Nunca commitear el archivo .env** con credenciales reales
6. **Usar usuarios no-root** en contenedores
7. **Implementar multi-stage builds** para imágenes más pequeñas (ya implementado)
8. **Versionar imágenes** en producción

## 🔐 Seguridad

- ✅ Cambiar `SECRET_KEY` en producción
- ✅ No exponer puertos innecesarios
- ✅ Usuarios no-root en contenedores
- ✅ Health checks configurados
- ⚠️ Actualizar imágenes base regularmente
- ⚠️ Escanear imágenes con `docker scan`

## 📚 Referencias

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI with Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs -f`
2. Verifica health checks: `docker compose ps`
3. Limpia y rebuild: `docker compose down -v && docker compose up -d --build`
4. Consulta la sección de troubleshooting arriba
5. Verifica que tu `.env` tenga `OPENAI_API_KEY` configurada
