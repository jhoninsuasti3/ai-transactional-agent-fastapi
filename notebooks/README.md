# Notebooks Directory

Este directorio contiene Jupyter notebooks para experimentación, análisis y desarrollo.

## Estructura

```
notebooks/
├── README.md              # Este archivo
├── experiments/           # Experimentos y pruebas
├── analysis/              # Análisis de datos y resultados
├── demos/                 # Demos y ejemplos
└── development/           # Notebooks de desarrollo
```

## Uso

### Iniciar Jupyter

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# Instalar jupyter si no está
uv pip install jupyter

# Iniciar Jupyter
jupyter notebook notebooks/
```

### Notebooks Comunes

1. **Agent Testing** - Probar agentes LangGraph
2. **Prompt Engineering** - Desarrollar y refinar prompts
3. **Data Analysis** - Analizar logs y transacciones
4. **API Testing** - Probar endpoints de la API

## Mejores Prácticas

### Organización
- Un notebook por experimento/tarea
- Nombres descriptivos (ej: `01_agent_conversation_testing.ipynb`)
- Usar markdown cells para documentación
- Limpiar outputs antes de commit (opcional)

### Código
```python
# Imports al inicio
import sys
sys.path.append('..')  # Para importar desde src/

from src.agents.transactional.agent import create_transactional_agent
from src.config.settings import settings

# Tu código aquí...
```

### Gitignore
Los notebooks con datos sensibles están en `.gitignore`:
```
notebooks/*.ipynb      # Todos los notebooks
!notebooks/README.md   # Excepto README
```

Para versionar un notebook específico:
```bash
# Agregar excepción en .gitignore
!notebooks/demos/demo_safe.ipynb
```

## Templates

### Template Básico
```python
# 1. Setup
import sys
sys.path.append('..')

# 2. Imports
from src.config.settings import settings

# 3. Configuration
# Configuración aquí

# 4. Main Code
# Tu código principal

# 5. Testing
# Tests y validaciones

# 6. Results
# Análisis de resultados
```

## Ejemplos Útiles

### Test de Agente
```python
from src.agents.transactional.agent import create_transactional_agent

agent = create_transactional_agent()

result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Envía $100 a 555-1234"}]
})

print(result)
```

### Test de API
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/chat",
        json={"message": "Hola"}
    )
    print(response.json())
```

## Recursos

- [Jupyter Documentation](https://jupyter.org/documentation)
- [IPython Tutorial](https://ipython.readthedocs.io/)
- [LangGraph Notebooks](https://github.com/langchain-ai/langgraph/tree/main/docs/docs/tutorials)

## Contribuir

Al crear notebooks:
1. Usa nombres descriptivos y numeración
2. Incluye documentación en markdown
3. Limpia outputs si contienen datos sensibles
4. Considera agregar al control de versiones si es útil para el equipo