# Code Quality Guidelines

## 🎯 Overview

Este proyecto mantiene altos estándares de calidad de código usando las siguientes herramientas:

- **Ruff**: Linter y formatter ultra-rápido (reemplaza black, isort, flake8, y más)
- **MyPy**: Type checking estático
- **Bandit**: Security scanning
- **Pre-commit**: Git hooks automáticos para validación antes de commit

---

## 🚀 Quick Start

### 1. Instalar Pre-commit

```bash
# El proyecto ya incluye pre-commit en las dev dependencies
uv sync

# Instalar los git hooks
uv run pre-commit install
```

### 2. Ejecutar Checks Manualmente

```bash
# Ejecutar todos los hooks en todos los archivos
uv run pre-commit run --all-files

# Ejecutar solo en archivos staged
uv run pre-commit run

# Ejecutar un hook específico
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files
```

---

## 🛠️ Herramientas de Calidad

### Ruff

Ruff es un linter y formatter extremadamente rápido escrito en Rust que reemplaza múltiples herramientas:
- **black** (formatting)
- **isort** (import sorting)
- **flake8** (linting)
- **pyupgrade** (Python upgrades)
- **y más...**

#### Comandos Ruff

```bash
# Linting
uv run ruff check apps/                    # Check código
uv run ruff check apps/ --fix              # Auto-fix issues
uv run ruff check apps/ --watch            # Watch mode

# Formatting
uv run ruff format apps/                   # Format código
uv run ruff format apps/ --check           # Check sin modificar
uv run ruff format apps/ --diff            # Ver diferencias

# Ambos
uv run ruff check apps/ --fix && uv run ruff format apps/
```

#### Reglas Habilitadas

```toml
[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "S",     # bandit security
    "B",     # flake8-bugbear
    "A",     # flake8-builtins
    "C4",    # flake8-comprehensions
    "DTZ",   # flake8-datetimez
    "T20",   # flake8-print
    "RET",   # flake8-return
    "SIM",   # flake8-simplify
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate (commented code)
    "PL",    # pylint
    "PERF",  # performance
]
```

#### Reglas Ignoradas

```toml
ignore = [
    "E501",    # line too long (handled by formatter)
    "S101",    # use of assert (OK in tests)
    "PLR0913", # too many arguments
    "PLR2004", # magic value in comparison
]
```

---

### MyPy

Type checker estático para Python.

#### Comandos MyPy

```bash
# Check todo apps/
uv run mypy apps/

# Check archivo específico
uv run mypy apps/orchestrator/api/app.py

# Con más información
uv run mypy apps/ --show-error-codes
uv run mypy apps/ --show-error-context
```

#### Configuración

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Nota**: Tests y alembic están excluidos de mypy checks.

---

### Bandit

Security linter para Python.

#### Comandos Bandit

```bash
# Scan completo
uv run bandit -r apps/

# Con reporte JSON
uv run bandit -r apps/ -f json -o bandit-report.json

# Solo severidad alta
uv run bandit -r apps/ -lll
```

---

## 🔧 Configuración de Editor

### VS Code

Instala las extensiones:
- **Ruff** (charliermarsh.ruff)
- **Python** (ms-python.python)
- **MyPy Type Checker** (ms-python.mypy-type-checker)

Agrega a `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",

  // Ruff
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },

  "ruff.lint.run": "onSave",
  "ruff.format.args": ["--line-length=100"],

  // MyPy
  "mypy-type-checker.importStrategy": "fromEnvironment",
  "mypy-type-checker.args": ["--ignore-missing-imports"],

  // Python
  "python.linting.enabled": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm / IntelliJ

1. Settings → Tools → External Tools
2. Agrega tool "Ruff Format":
   - Program: `$ProjectFileDir$/.venv/bin/ruff`
   - Arguments: `format $FilePath$`
   - Working directory: `$ProjectFileDir$`

3. Agrega tool "Ruff Check":
   - Program: `$ProjectFileDir$/.venv/bin/ruff`
   - Arguments: `check $FilePath$ --fix`
   - Working directory: `$ProjectFileDir$`

---

## 📋 Pre-commit Hooks

Los hooks se ejecutan automáticamente antes de cada commit.

### Hooks Configurados

1. **Ruff Linter** - Auto-fix linting issues
2. **Ruff Format** - Format code
3. **MyPy** - Type checking (solo apps/, no tests)
4. **File checks**:
   - Check large files
   - Check merge conflicts
   - Check YAML/JSON/TOML syntax
   - Fix trailing whitespace
   - Fix line endings
5. **Bandit** - Security checks
6. **Safety** - Dependency vulnerability check

### Bypass Hooks (Solo cuando necesario)

```bash
# Skip todos los hooks
git commit -m "mensaje" --no-verify

# Skip hook específico
SKIP=mypy git commit -m "mensaje"

# Skip múltiples hooks
SKIP=mypy,bandit git commit -m "mensaje"
```

**⚠️ Advertencia**: Solo usa `--no-verify` cuando realmente sea necesario. Los hooks están ahí para ayudarte.

---

## 🔍 Common Issues

### Issue 1: MyPy falla por imports faltantes

**Problema**:
```
error: Cannot find implementation or library stub for module named 'langchain'
```

**Solución**:
```bash
# Reinstalar dependencias
uv sync

# O ignorar imports específicos en pyproject.toml
[[tool.mypy.overrides]]
module = ["langchain.*"]
ignore_missing_imports = true
```

### Issue 2: Pre-commit muy lento

**Problema**: Pre-commit toma mucho tiempo.

**Solución**:
```bash
# Solo ejecutar en archivos modificados (default)
git commit

# Actualizar hooks
uv run pre-commit autoupdate

# Limpiar cache
uv run pre-commit clean
```

### Issue 3: Ruff y Black/isort en conflicto

**Problema**: Si tienes black o isort configurados, pueden entrar en conflicto.

**Solución**: Ruff reemplaza a ambos. Remover black e isort:
```bash
# Desinstalar (si están instalados)
uv pip uninstall black isort

# Usar solo Ruff
uv run ruff format apps/
```

### Issue 4: Type hints complejos

**Problema**: MyPy se queja de types complejos.

**Solución**: Usar `# type: ignore` solo cuando realmente sea necesario:
```python
from typing import Any

result: Any = complex_function()  # type: ignore[no-any-return]
```

---

## 📊 CI/CD Integration

Los checks de calidad se ejecutan automáticamente en CI:

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    name: Code Quality & Linting
    steps:
      - name: Run ruff linter
      - name: Run ruff formatter check
      - name: Run mypy type checking
      - name: Run bandit security checks
```

**Importante**: El CI falla si:
- ✅ Ruff check falla
- ✅ Ruff format check falla (código no formateado)
- ⚠️ MyPy encuentra errores (warning, no bloquea)
- ⚠️ Bandit encuentra issues (warning, no bloquea)

---

## 🎯 Best Practices

### 1. Format antes de commit
```bash
uv run ruff check apps/ --fix
uv run ruff format apps/
git add .
git commit -m "..."
```

### 2. Type hints en funciones nuevas
```python
# ✅ Bueno
def process_transaction(phone: str, amount: int) -> dict[str, Any]:
    ...

# ❌ Malo
def process_transaction(phone, amount):
    ...
```

### 3. Usar `# noqa` con razón
```python
# ✅ Bueno - explica por qué
SECRET_KEY = "default"  # noqa: S105  # Safe default, overridden by env

# ❌ Malo - sin explicación
SECRET_KEY = "default"  # noqa: S105
```

### 4. Imports organizados
Ruff los organiza automáticamente, pero sigue este orden:
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local
from apps.orchestrator.settings import settings
```

---

## 📚 Referencias

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## 🆘 Help

Si tienes problemas con las herramientas de calidad:

1. Lee el error completo
2. Busca en esta documentación
3. Consulta la documentación oficial de la herramienta
4. Pregunta al equipo

**No uses `--no-verify` o `# noqa` sin entender el problema primero.**
