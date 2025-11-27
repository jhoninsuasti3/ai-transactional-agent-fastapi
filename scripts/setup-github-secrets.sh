#!/bin/bash
#
# Script para configurar GitHub Secrets de forma automática
# Requiere: GitHub CLI (gh) instalado y autenticado
#
# Uso: ./scripts/setup-github-secrets.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}GitHub Secrets Setup${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Verificar que gh esté instalado
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) no está instalado${NC}"
    echo "Instalar con: brew install gh (macOS) o apt install gh (Ubuntu)"
    exit 1
fi

# Verificar autenticación
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ No estás autenticado en GitHub CLI${NC}"
    echo "Ejecutar: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI configurado correctamente${NC}"
echo ""

# Función para añadir secret
add_secret() {
    local name=$1
    local value=$2
    local required=$3

    if [ -z "$value" ]; then
        if [ "$required" == "true" ]; then
            echo -e "${RED}❌ $name es obligatorio${NC}"
            return 1
        else
            echo -e "${YELLOW}⚠️  $name vacío (opcional), saltando...${NC}"
            return 0
        fi
    fi

    echo -n "Configurando $name... "
    if echo "$value" | gh secret set "$name"; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

# Pedir confirmación
echo -e "${YELLOW}Este script va a configurar los secrets de GitHub${NC}"
echo -e "${YELLOW}¿Continuar? (y/n)${NC}"
read -r response
if [ "$response" != "y" ]; then
    echo "Cancelado"
    exit 0
fi

echo ""
echo "=================================="
echo "📝 Ingresa los valores de los secrets"
echo "=================================="
echo ""

# OpenAI
echo -e "${GREEN}[OpenAI Configuration]${NC}"
read -p "OPENAI_API_KEY (sk-proj-xxxxx): " OPENAI_API_KEY
echo ""

# AWS
echo -e "${GREEN}[AWS Configuration]${NC}"
read -p "AWS_ACCESS_KEY_ID (AKIAxxxxx): " AWS_ACCESS_KEY_ID
read -p "AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY
echo ""

# Database
echo -e "${GREEN}[Database Configuration]${NC}"
read -p "PROD_POSTGRES_HOST (your-rds.amazonaws.com): " PROD_POSTGRES_HOST
read -p "PROD_POSTGRES_USER (postgres): " PROD_POSTGRES_USER
read -sp "PROD_POSTGRES_PASSWORD: " PROD_POSTGRES_PASSWORD
echo ""
read -p "PROD_POSTGRES_DB (ai_agent_prod): " PROD_POSTGRES_DB
echo ""

# Application
echo -e "${GREEN}[Application Configuration]${NC}"
read -sp "SECRET_KEY (32+ caracteres): " SECRET_KEY
echo ""
read -p "CORS_ORIGINS (https://yourdomain.com): " CORS_ORIGINS
read -p "TRANSACTION_SERVICE_URL (http://localhost:8001): " TRANSACTION_SERVICE_URL
echo ""

# Optional
echo -e "${GREEN}[Optional Configuration]${NC}"
read -p "CODECOV_TOKEN (opcional): " CODECOV_TOKEN
read -p "SLACK_WEBHOOK_URL (opcional): " SLACK_WEBHOOK_URL
read -p "APP_URL (opcional): " APP_URL
echo ""

# EC2 (opcional)
echo -e "${YELLOW}¿Configurar EC2 deployment? (y/n)${NC}"
read -r ec2_response
if [ "$ec2_response" == "y" ]; then
    read -p "EC2_HOST (ec2-xx-xx-xx-xx.compute-1.amazonaws.com): " EC2_HOST
    echo "EC2_SSH_PRIVATE_KEY (pega el contenido de la clave privada, termina con línea vacía):"
    EC2_SSH_PRIVATE_KEY=$(cat)
fi

echo ""
echo "=================================="
echo "🚀 Configurando secrets en GitHub..."
echo "=================================="
echo ""

# Configurar secrets requeridos
add_secret "OPENAI_API_KEY" "$OPENAI_API_KEY" true || exit 1
add_secret "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID" true || exit 1
add_secret "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY" true || exit 1
add_secret "PROD_POSTGRES_HOST" "$PROD_POSTGRES_HOST" true || exit 1
add_secret "PROD_POSTGRES_USER" "$PROD_POSTGRES_USER" true || exit 1
add_secret "PROD_POSTGRES_PASSWORD" "$PROD_POSTGRES_PASSWORD" true || exit 1
add_secret "PROD_POSTGRES_DB" "$PROD_POSTGRES_DB" true || exit 1
add_secret "SECRET_KEY" "$SECRET_KEY" true || exit 1
add_secret "CORS_ORIGINS" "$CORS_ORIGINS" true || exit 1
add_secret "TRANSACTION_SERVICE_URL" "$TRANSACTION_SERVICE_URL" true || exit 1

# Configurar secrets opcionales
add_secret "CODECOV_TOKEN" "$CODECOV_TOKEN" false
add_secret "SLACK_WEBHOOK_URL" "$SLACK_WEBHOOK_URL" false
add_secret "APP_URL" "$APP_URL" false

if [ "$ec2_response" == "y" ]; then
    add_secret "EC2_HOST" "$EC2_HOST" false
    add_secret "EC2_SSH_PRIVATE_KEY" "$EC2_SSH_PRIVATE_KEY" false
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ Secrets configurados exitosamente${NC}"
echo "=================================="
echo ""
echo "Puedes ver los secrets configurados en:"
echo "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/settings/secrets/actions"
echo ""
echo -e "${GREEN}🎉 ¡Listo! Ya puedes hacer push y los workflows se ejecutarán${NC}"
