#!/bin/bash
#
# Script para probar pre-commit hooks sin hacer commit
# Uso: ./scripts/test-precommit.sh
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Pre-commit Hooks Test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. Verificar que pre-commit esté instalado
echo -e "${YELLOW}[1/5]${NC} Verificando instalación de pre-commit..."
if ! command -v pre-commit &> /dev/null; then
    echo -e "${RED}❌ pre-commit no está instalado${NC}"
    echo "Instalar con: uv run pre-commit install"
    exit 1
fi
echo -e "${GREEN}✅ pre-commit instalado${NC}"
echo ""

# 2. Verificar hooks instalados
echo -e "${YELLOW}[2/5]${NC} Verificando hooks instalados..."
if [ ! -f .git/hooks/pre-commit ]; then
    echo -e "${YELLOW}⚠️  Hooks no instalados${NC}"
    echo "Instalando hooks..."
    uv run pre-commit install
    echo -e "${GREEN}✅ Hooks instalados${NC}"
else
    echo -e "${GREEN}✅ Hooks ya instalados${NC}"
fi
echo ""

# 3. Ejecutar ruff linter
echo -e "${YELLOW}[3/5]${NC} Ejecutando Ruff linter..."
if uv run ruff check apps/ --output-format=concise; then
    echo -e "${GREEN}✅ Ruff check pasó${NC}"
else
    echo -e "${RED}❌ Ruff check falló${NC}"
    echo "Corregir con: uv run ruff check apps/ --fix"
    exit 1
fi
echo ""

# 4. Ejecutar ruff formatter
echo -e "${YELLOW}[4/5]${NC} Verificando formato de código..."
if uv run ruff format --check apps/; then
    echo -e "${GREEN}✅ Código está formateado correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Código necesita formato${NC}"
    echo "Formatear con: uv run ruff format apps/"
    exit 1
fi
echo ""

# 5. Ejecutar pre-commit en todos los archivos
echo -e "${YELLOW}[5/5]${NC} Ejecutando todos los pre-commit hooks..."
echo ""
# Run with SKIP=mypy to skip type checking for now
if SKIP=mypy uv run pre-commit run --all-files; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ Todos los hooks críticos pasaron!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  MyPy type checking fue skipped (hay 99 warnings)${NC}"
    echo -e "${YELLOW}   Puedes corregirlos gradualmente ejecutando: uv run mypy apps/${NC}"
    echo ""
    echo -e "${BLUE}Tu código está listo para commit 🚀${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}❌ Algunos hooks fallaron${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "  uv run ruff check apps/ --fix      # Auto-fix linting"
    echo "  uv run ruff format apps/           # Format código"
    echo "  uv run mypy apps/                  # Type checking (warnings only)"
    echo "  uv run pre-commit run --all-files  # Ejecutar todos los hooks"
    echo ""
    echo -e "${YELLOW}Ver documentación en: docs/CODE_QUALITY.md${NC}"
    exit 1
fi
