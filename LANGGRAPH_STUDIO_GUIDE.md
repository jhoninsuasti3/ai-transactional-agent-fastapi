# Guía: LangGraph Studio - Visualización del Agente

## ¿Qué es LangGraph Studio?

LangGraph Studio es una herramienta visual de desarrollo que te permite:
- ✅ Ver el grafo de nodos y edges visualmente
- ✅ Ejecutar el agente paso a paso (debuggear)
- ✅ Inspeccionar el estado en cada nodo
- ✅ Ver el historial de mensajes
- ✅ Probar diferentes inputs interactivamente

## Opción 1: LangGraph CLI (`langgraph dev`)

### Paso 1: Crear archivo de configuración

Necesitas un archivo `langgraph.json` en la raíz del proyecto:

```json
{
  "dependencies": ["."],
  "graphs": {
    "transactional_agent": "./apps/agents/transactional/graph.py:agent"
  },
  "env": ".env"
}
```

### Paso 2: Levantar LangGraph Studio

```bash
# En una terminal separada (Terminal 4)
cd /home/jhonmo/apps/retos/ai-transactional-agent-fastapi

# Levantar LangGraph Studio
uv run langgraph dev

# Se abrirá en: http://localhost:8123
```

### Paso 3: Acceder al Studio

1. Abre tu navegador en `http://localhost:8123`
2. Verás la interfaz gráfica con tu agente
3. Podrás ver los nodos: `conversation`, `extract`, `validate`, `confirmation`, `transaction`
4. Las flechas muestran los edges condicionales

### Paso 4: Probar el agente

En la interfaz puedes:
- Escribir mensajes en el chat
- Ver el estado actual en cada paso
- Inspeccionar qué nodo se ejecutó
- Ver los valores de `phone`, `amount`, `needs_confirmation`, etc.

## Opción 2: Exportar imagen del grafo (sin servidor)

Si solo quieres ver el grafo estático sin correr el servidor:

```python
# Crear script: visualize_graph.py
from apps.agents.transactional.graph import agent

# Generar imagen PNG
agent.get_graph().draw_mermaid_png(output_file_path="agent_graph.png")

print("Grafo guardado en: agent_graph.png")
```

Ejecutar:
```bash
uv run python visualize_graph.py
```

Esto genera una imagen PNG con el grafo completo.

## Opción 3: Mermaid Diagram (Markdown)

Puedes exportar el grafo como diagrama Mermaid para documentación:

```python
# Crear script: export_mermaid.py
from apps.agents.transactional.graph import agent

# Generar código Mermaid
mermaid_code = agent.get_graph().draw_mermaid()

print(mermaid_code)

# Guardar en archivo
with open("agent_graph.mmd", "w") as f:
    f.write(mermaid_code)

print("Diagrama guardado en: agent_graph.mmd")
```

Ejecutar:
```bash
uv run python export_mermaid.py
```

Luego puedes visualizarlo en:
- [Mermaid Live Editor](https://mermaid.live/)
- VS Code con extensión "Markdown Preview Mermaid Support"
- GitHub (renderiza Mermaid automáticamente)

## Configuración Completa para LangGraph Studio

### 1. Crear `langgraph.json`

```json
{
  "dependencies": ["."],
  "graphs": {
    "transactional_agent": "./apps/agents/transactional/graph.py:agent"
  },
  "env": ".env",
  "python_version": "3.12"
}
```

### 2. Asegurarte que `.env` tenga las variables necesarias

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transactional_agent
LANGGRAPH_CHECKPOINT_DB=postgresql+psycopg://postgres:postgres@localhost:5432/transactional_agent

# LLM
ANTHROPIC_API_KEY=tu-api-key
LLM_MODEL=anthropic:claude-3-5-haiku-20241022

# Mock API
TRANSACTION_SERVICE_URL=http://localhost:8001
```

### 3. Levantar todos los servicios

**Terminal 1: PostgreSQL**
```bash
docker compose up -d postgres
```

**Terminal 2: Mock API**
```bash
uv run uvicorn mock_api.main:app --port 8001 --reload
```

**Terminal 3: Orchestrator** (opcional si solo usas Studio)
```bash
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload
```

**Terminal 4: LangGraph Studio**
```bash
uv run langgraph dev
```

## Estructura del Grafo Transactional Agent

Cuando abras LangGraph Studio verás algo así:

```
┌─────────────┐
│ conversation│ (entry point)
└──────┬──────┘
       │
       ├─────────────┐
       ▼             ▼
   ┌────────┐     ┌─────┐
   │ extract│     │ END │ (conversación simple)
   └───┬────┘     └─────┘
       │
       ├─────────────┐
       ▼             ▼
  ┌─────────┐   ┌────────────┐
  │ validate│   │conversation│ (datos incompletos)
  └────┬────┘   └────────────┘
       │
       ├──────────┐
       ▼          ▼
┌──────────────┐ ┌─────┐
│ confirmation │ │ END │ (error)
└──────┬───────┘ └─────┘
       │
       ├──────────┐
       ▼          ▼
┌─────────────┐ ┌─────┐
│ transaction │ │ END │ (no confirmado)
└──────┬──────┘ └─────┘
       │
       ▼
    ┌─────┐
    │ END │
    └─────┘
```

## Funcionalidades de LangGraph Studio

### 1. Visualización del Grafo
- Nodos en color azul/verde
- Edges condicionales con labels
- Entry point marcado
- Nodos terminales (END)

### 2. Playground Interactivo
- Input de texto para simular mensajes de usuario
- Botón "Run" para ejecutar el agente
- Ver output en cada nodo
- Inspeccionar estado completo

### 3. Historial y Replay
- Ver todas las ejecuciones anteriores
- Replay de conversaciones
- Comparar estados entre ejecuciones

### 4. State Inspector
- Ver valores de cada campo del estado:
  - `messages`: Array de mensajes
  - `phone`: Teléfono extraído
  - `amount`: Monto extraído
  - `needs_confirmation`: Bool
  - `confirmed`: Bool
  - `transaction_id`: ID de transacción
  - `transaction_status`: Estado

### 5. Debugging Step-by-Step
- Ejecutar nodo por nodo
- Pausar en breakpoints
- Inspeccionar valores intermedios

## Troubleshooting

### Error: "Could not find graph"

Asegúrate que `langgraph.json` apunte correctamente:
```json
{
  "graphs": {
    "transactional_agent": "./apps/agents/transactional/graph.py:agent"
    // ↑ Debe ser la ruta relativa desde raíz del proyecto
  }
}
```

### Error: "Module not found"

```bash
# Asegúrate de estar en la raíz del proyecto
cd /home/jhonmo/apps/retos/ai-transactional-agent-fastapi

# Instalar dependencias
uv sync

# Correr langgraph dev
uv run langgraph dev
```

### Puerto 8123 ocupado

```bash
# Ver qué proceso usa el puerto
lsof -i :8123

# Matar el proceso
kill -9 <PID>

# O usar otro puerto
uv run langgraph dev --port 8124
```

### No se ve el grafo

1. Verifica que el archivo `graph.py` exporta correctamente el agente
2. Asegúrate que el agente está compilado: `agent = create_graph()`
3. Revisa logs en la terminal donde corriste `langgraph dev`

## Comparación: LangGraph Studio vs Orchestrator API

| Característica | LangGraph Studio | Orchestrator API |
|---------------|------------------|------------------|
| Uso | Desarrollo/Debug | Producción |
| Puerto | 8123 | 8002 |
| Visualización | ✅ Sí | ❌ No |
| Debugging | ✅ Step-by-step | ❌ Solo logs |
| Checkpoints | ✅ PostgreSQL | ✅ PostgreSQL |
| API REST | ❌ No (Playground) | ✅ Sí |
| Hot Reload | ✅ Sí | ✅ Sí (con --reload) |

## Recomendación

**Para desarrollo:**
- Usa LangGraph Studio (`langgraph dev`) para visualizar y debuggear
- Prueba flujos complejos y ve el estado en cada paso
- Valida que los edges condicionales funcionen correctamente

**Para testing de integración:**
- Usa Orchestrator API (`uvicorn`) para probar endpoints
- Simula requests desde un cliente real
- Valida la respuesta JSON completa

**Puedes correr ambos simultáneamente:**
- Terminal 4: `langgraph dev` (puerto 8123) - para debuggear
- Terminal 3: `uvicorn ... --port 8002` - para testing API

## Recursos Adicionales

- [LangGraph Studio Docs](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)
- [LangGraph Visualization](https://langchain-ai.github.io/langgraph/how-tos/visualization/)
- [Debugging Guide](https://langchain-ai.github.io/langgraph/how-tos/debug/)

---

## Resumen de Comandos

```bash
# 1. Crear langgraph.json (ver arriba)

# 2. Levantar servicios
docker compose up -d postgres                          # Terminal 1
uv run uvicorn mock_api.main:app --port 8001 --reload # Terminal 2

# 3. Opción A: Solo LangGraph Studio
uv run langgraph dev                                   # Terminal 4

# 3. Opción B: Ambos (Studio + API)
uv run langgraph dev                                   # Terminal 4
uv run uvicorn apps.orchestrator.api.app:app --port 8002 --reload # Terminal 3

# 4. Abrir navegador
# Studio: http://localhost:8123
# API: http://localhost:8002/health
```

**¡Ahora puedes ver tu agente gráficamente!** 🎨📊
