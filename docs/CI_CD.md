# CI/CD Setup Guide

## 📋 Tabla de Contenidos

1. [Resumen](#resumen)
2. [Configuración de GitHub](#configuración-de-github)
3. [Configuración de AWS](#configuración-de-aws)
4. [Configuración de Secrets](#configuración-de-secrets)
5. [Workflows Disponibles](#workflows-disponibles)
6. [Deployment Manual](#deployment-manual)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen

Este proyecto incluye 3 workflows de CI/CD:

### CI (Continuous Integration) - `ci.yml`
✅ **Activo** - Se ejecuta en cada push/PR a `main` o `develop`
- **Linting**: Ruff para calidad de código
- **Tests**: Unitarios + integración con PostgreSQL (420 tests)
- **Coverage**: Verificación dedicada ≥70% (actualmente 80%)
- **Security**: Bandit + Safety scan
- **Build**: Validación de imagen Docker

**Estado**: ✅ Pipeline completamente funcional

### CD AWS ECS - `cd-aws.yml`
🔒 **Deshabilitado** - Deploy a AWS ECS/Fargate
- Build y push a ECR
- Deploy a ECS con rolling update
- Smoke tests post-deployment
- Notificaciones Slack

**Estado**: 📋 Código base listo
- ⏳ Requiere ajustes en Terraform
- ⏳ Requiere configuración AWS + GitHub Secrets
- ⏳ Requiere pruebas end-to-end

### CD AWS EC2 - `cd-ec2.yml`
🔒 **Deshabilitado** - Deploy a instancia EC2
- Deploy directo con SSH
- Backup automático
- Rollback en caso de fallo

**Estado**: 📋 Código base listo
- ⏳ Requiere provisionar instancia EC2
- ⏳ Requiere configurar SSH keys
- ⏳ Requiere pruebas end-to-end

---

## 🏗️ Infrastructure as Code (IaC)

El proyecto incluye infraestructura básica definida con **Terraform** en `aws/terraform/`:

### Componentes Terraform existentes:
- 📝 **VPC** con subnets públicas y privadas
- 📝 **RDS PostgreSQL** configuración básica
- 📝 **ECS Cluster** para containers
- 📝 **Security Groups** y networking
- 📝 **IAM Roles** y políticas
- 📝 **S3 backend** para Terraform state

### Tareas pendientes para CD completo:

**Terraform:**
- ⏳ Validar y ajustar configuraciones de recursos
- ⏳ Completar variables faltantes (endpoints, ARNs, etc.)
- ⏳ Añadir outputs necesarios para CD workflows
- ⏳ Probar `terraform plan` y `terraform apply`
- ⏳ Configurar remote state (bucket S3)

**AWS:**
- ⏳ Crear y configurar IAM user para GitHub Actions
- ⏳ Configurar AWS credentials (ACCESS_KEY, SECRET_KEY)
- ⏳ Crear bucket S3 para Terraform state
- ⏳ Provisionar infraestructura inicial con Terraform

**GitHub Secrets:**
- ⏳ Agregar `AWS_ACCESS_KEY_ID`
- ⏳ Agregar `AWS_SECRET_ACCESS_KEY`
- ⏳ Agregar variables de producción (DB, endpoints)

**CD Workflows:**
- ⏳ Remover `if: false` de jobs de deploy
- ⏳ Ajustar nombres de recursos AWS en workflows
- ⏳ Probar workflow completo en staging

**Estado**: 📋 Código base listo, requiere configuración y pruebas end-to-end

---

## 🔧 Configuración de GitHub

### 1. Habilitar GitHub Actions

1. Ve a tu repositorio en GitHub
2. Settings → Actions → General
3. Selecciona "Allow all actions and reusable workflows"

### 2. Configurar Secrets

Ve a **Settings → Secrets and variables → Actions** y añade:

#### Secrets Requeridos (Obligatorios)

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxx

# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx

# Database (Production)
PROD_POSTGRES_HOST=your-rds-endpoint.rds.amazonaws.com
PROD_POSTGRES_USER=postgres
PROD_POSTGRES_PASSWORD=your-secure-password
PROD_POSTGRES_DB=ai_agent_prod

# Application
SECRET_KEY=your-super-secret-key-min-32-chars
CORS_ORIGINS=https://yourdomain.com
TRANSACTION_SERVICE_URL=https://api.yourdomain.com/transactions
```

#### Secrets Opcionales

```bash
# Codecov (para reportes de cobertura)
CODECOV_TOKEN=xxxxx

# Slack (para notificaciones)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx

# EC2 Deploy (si usas EC2)
EC2_HOST=ec2-xx-xx-xx-xx.compute-1.amazonaws.com
EC2_SSH_PRIVATE_KEY=<paste-your-complete-ssh-private-key-content-here>

# Application URL (para smoke tests)
APP_URL=https://api.yourdomain.com
```

### 3. Configurar Environments (Opcional)

Para deploys con aprobación manual:

1. Settings → Environments → New environment
2. Nombre: `staging` o `production`
3. Configurar:
   - ✅ Required reviewers (para production)
   - ✅ Wait timer (opcional)
   - ✅ Deployment branches (solo `main`)

---

## ☁️ Configuración de AWS

### Opción 1: AWS ECS/Fargate (Recomendado)

#### Requisitos previos

1. Cuenta de AWS
2. AWS CLI instalado
3. Terraform instalado (opcional, para infra as code)

#### Paso 1: Crear infraestructura con Terraform

```bash
cd aws/terraform

# Inicializar Terraform
terraform init

# Crear archivo de variables
cat > terraform.tfvars << EOF
aws_region      = "us-east-1"
environment     = "production"
db_username     = "postgres"
db_password     = "YOUR_SECURE_PASSWORD"
openai_api_key  = "YOUR_OPENAI_KEY"
EOF

# Planificar cambios
terraform plan

# Aplicar infraestructura
terraform apply
```

Esto creará:
- ✅ VPC con subnets públicas y privadas
- ✅ RDS PostgreSQL
- ✅ ECR (Docker registry)
- ✅ ECS Cluster
- ✅ Application Load Balancer
- ✅ Security Groups
- ✅ IAM Roles
- ✅ CloudWatch Logs
- ✅ Secrets Manager

#### Paso 2: Configurar ECS Service

```bash
# Crear ECS Service
aws ecs create-service \
  --cluster ai-transactional-agent-cluster-production \
  --service-name ai-transactional-agent-service \
  --task-definition ai-transactional-agent-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=ai-transactional-agent,containerPort=8000"
```

#### Paso 3: Configurar Secrets Manager

```bash
# Crear secrets
aws secretsmanager create-secret \
  --name ai-agent/openai-api-key \
  --secret-string "sk-proj-xxxxx"

aws secretsmanager create-secret \
  --name ai-agent/database-url \
  --secret-string "postgresql+asyncpg://user:pass@host:5432/db"

aws secretsmanager create-secret \
  --name ai-agent/checkpoint-url \
  --secret-string "postgresql://user:pass@host:5432/db"

aws secretsmanager create-secret \
  --name ai-agent/secret-key \
  --secret-string "your-secret-key-here"
```

### Opción 2: AWS EC2

#### Paso 1: Lanzar instancia EC2

```bash
# Crear instancia
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ai-transactional-agent}]'
```

#### Paso 2: Configurar instancia

```bash
# Conectar por SSH
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com

# Instalar dependencias
sudo apt update
sudo apt install -y python3.12 python3.12-venv postgresql-client

# Instalar uv
curl -LsSf https://astral.sh/uv/0.4.18/install.sh | sh

# Crear servicio systemd
sudo tee /etc/systemd/system/ai-transactional-agent.service > /dev/null << EOF
[Unit]
Description=AI Transactional Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-transactional-agent
Environment="PATH=/home/ubuntu/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/ai-transactional-agent/.venv/bin/uvicorn apps.orchestrator.api.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar servicio
sudo systemctl enable ai-transactional-agent
sudo systemctl start ai-transactional-agent
```

---

## 🔐 Configuración de Secrets

### Variables de Entorno Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key de OpenAI | `sk-proj-xxxxx` |
| `DATABASE_URL` | URL de PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `LANGGRAPH_CHECKPOINT_URL` | URL para checkpoints | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Clave secreta (32+ chars) | `super-secret-key-xxxxx` |
| `ENVIRONMENT` | Ambiente | `production` o `staging` |
| `LOG_LEVEL` | Nivel de logs | `INFO` |
| `CORS_ORIGINS` | Orígenes permitidos | `https://yourdomain.com` |
| `TRANSACTION_SERVICE_URL` | URL del servicio de transacciones | `http://localhost:8001` |

---

## 🚀 Workflows Disponibles

### CI Workflow (`ci.yml`) ✅

**Trigger:** Push o PR a `main`/`develop`

**Jobs:**
1. **lint** - Verificación de código (ruff, mypy)
2. **test** - Tests unitarios + integración con PostgreSQL
3. **security** - Escaneo de seguridad (bandit, safety)
4. **coverage** - Verificación independiente de cobertura ≥70%
5. **build** - Validación de imagen Docker (Dockerfile.orchestrator)
6. **summary** - Resumen y validación de todos los jobs

**Criterio de éxito:**
- ✅ Linting sin errores
- ✅ 420 tests pasando
- ✅ Coverage ≥70% (actualmente 80%)
- ✅ Sin vulnerabilidades críticas
- ✅ Dockerfile valida

**Gestión de dependencias:** `uv 0.5.11` con `pyproject.toml`

### CD AWS ECS Workflow (`cd-aws.yml`) 🔒

**Trigger:**
- Después de CI exitoso (workflow_run)
- Manual dispatch

**Jobs activos:**
1. **check-ci** - Verifica que CI haya pasado
2. **test** - Safety check adicional

**Jobs deshabilitados (requieren AWS):**
- ~~build-and-push~~ - Build y push a ECR
- ~~deploy-ecs~~ - Deploy a ECS Fargate
- ~~smoke-test~~ - Health checks
- ~~notify~~ - Notificaciones Slack

**Para activar:** Configurar AWS credentials y remover `if: false`

### CD EC2 Workflow (`cd-ec2.yml`) 🔒

**Trigger:**
- Después de CI exitoso (workflow_run)
- Manual dispatch

**Jobs activos:**
1. **check-ci** - Verifica que CI haya pasado
2. **test** - Safety check adicional

**Jobs deshabilitados (requieren EC2):**
- ~~deploy~~ - Deploy a EC2 con SSH
- ~~rollback~~ - Rollback automático

**Para activar:** Configurar instancia EC2 y SSH keys, remover `if: false`

---

## 🛠️ Deployment Manual

### Deploy a ECS (Manual)

```bash
# 1. Build image
docker build -t ai-transactional-agent .

# 2. Tag image
docker tag ai-transactional-agent:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-transactional-agent:latest

# 3. Login a ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 4. Push image
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-transactional-agent:latest

# 5. Update service
aws ecs update-service \
  --cluster ai-transactional-agent-cluster \
  --service ai-transactional-agent-service \
  --force-new-deployment
```

### Deploy a EC2 (Manual)

```bash
# 1. Conectar por SSH
ssh ubuntu@your-ec2-host

# 2. Actualizar código
cd /home/ubuntu/ai-transactional-agent
git pull origin main

# 3. Instalar dependencias
source .venv/bin/activate
uv pip install -r requirements.txt

# 4. Reiniciar servicio
sudo systemctl restart ai-transactional-agent

# 5. Verificar estado
sudo systemctl status ai-transactional-agent
curl http://localhost:8000/health
```

---

## 🔍 Troubleshooting

### Tests fallan en CI

```bash
# Verificar localmente
uv run pytest tests/ --cov=apps --cov-fail-under=70

# Ver logs detallados
uv run pytest tests/ -v --tb=short
```

### Deploy a ECS falla

```bash
# Ver logs del task
aws ecs describe-tasks \
  --cluster ai-transactional-agent-cluster \
  --tasks TASK_ID

# Ver logs de CloudWatch
aws logs tail /ecs/ai-transactional-agent --follow
```

### Health check falla

```bash
# Verificar endpoint
curl -v http://your-alb-url/health

# Verificar logs
aws logs tail /ecs/ai-transactional-agent --follow
```

### Rollback manual

#### ECS
```bash
# Listar task definitions
aws ecs list-task-definitions \
  --family-prefix ai-transactional-agent

# Actualizar a versión anterior
aws ecs update-service \
  --cluster ai-transactional-agent-cluster \
  --service ai-transactional-agent-service \
  --task-definition ai-transactional-agent-task:PREVIOUS_VERSION
```

#### EC2
```bash
# SSH a la instancia
ssh ubuntu@your-ec2-host

# Restaurar backup
BACKUP_DIR=/home/ubuntu/backups/ai-transactional-agent-YYYYMMDD-HHMMSS
sudo rm -rf /home/ubuntu/ai-transactional-agent
sudo cp -r $BACKUP_DIR /home/ubuntu/ai-transactional-agent
sudo systemctl restart ai-transactional-agent
```

---

## 📊 Monitoreo

### CloudWatch Dashboards

Crear dashboard para monitorear:
- CPU/Memory utilization
- Request count
- Response times
- Error rates

### Alertas

Configurar alarmas para:
- Health check failures
- High error rate (>5%)
- High latency (>2s p99)
- Low task count

---

## 🔗 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
