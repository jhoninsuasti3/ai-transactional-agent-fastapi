# Prompts Directory

Este directorio contiene todos los prompts y plantillas utilizados en el proyecto.

## Estructura

```
prompts/
├── README.md          # Este archivo
├── PROMPTS.md         # Colección principal de prompts
├── agents/            # Prompts para agentes
│   ├── transactional/ # Prompts del agente transaccional
│   └── shared/        # Prompts compartidos
└── templates/         # Plantillas reutilizables
```

## Uso

### Para Agentes LangGraph

Los prompts se organizan por agente y por nodo:

```python
from src.agents.transactional.prompts import CONVERSATION_PROMPT

# Usar en un nodo
response = llm.invoke(CONVERSATION_PROMPT.format(
    context=context,
    message=user_message
))
```

### Para Desarrollo

Consultar `PROMPTS.md` para ver todos los prompts disponibles y ejemplos de uso.

## Mejores Prácticas

1. **Versionado**: Mantén versiones de prompts importantes
2. **Documentación**: Documenta el propósito y contexto de cada prompt
3. **Testing**: Testea prompts con diferentes inputs
4. **Iteración**: Refina prompts basándote en resultados reales

## Prompts por Categoría

### Agente Transaccional
- Extracción de entidades
- Validación de transacciones
- Conversación general
- Confirmación de transacciones

### Prompts del Sistema
- Contexto del asistente
- Reglas de negocio
- Límites y restricciones

## Contribuir

Al agregar nuevos prompts:
1. Usa nombres descriptivos
2. Incluye ejemplos de uso
3. Documenta parámetros esperados
4. Agrega al índice en PROMPTS.md
