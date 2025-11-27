"""Script para visualizar el grafo del agente transaccional."""
from apps.agents.transactional.graph import agent

# Generar imagen PNG del grafo
try:
    agent.get_graph().draw_mermaid_png(output_file_path="agent_graph.png")
    print("✅ Grafo guardado en: agent_graph.png")
    print("Abre el archivo para ver la visualización del agente")
except Exception as e:
    print(f"❌ Error generando grafo: {e}")
    print("\nIntentando exportar como Mermaid text...")
    
    # Plan B: Exportar como texto Mermaid
    mermaid = agent.get_graph().draw_mermaid()
    with open("agent_graph.mmd", "w") as f:
        f.write(mermaid)
    print("✅ Diagrama Mermaid guardado en: agent_graph.mmd")
    print("Copia el contenido y pégalo en: https://mermaid.live/")
