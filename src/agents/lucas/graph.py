import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .state import State
from .tools import cadastrar_cliente, consultar_base_de_conhecimento
from .nodes import (
    agente_cadastro,
    roteador_semantico,
    agente_bate_papo,
    agente_especialista,
)


# ==========================================
# 5. CONSTRUÇÃO DO GRAFO (Arquitetura)
# ==========================================
# ==========================================
# 5. CONSTRUÇÃO DO GRAFO (Arquitetura)
# ==========================================
graph_builder = StateGraph(State)

# 1. Adicionando todos os Nós Principais
graph_builder.add_node("chat_node", agente_bate_papo)
graph_builder.add_node("especialista_node", agente_especialista)
graph_builder.add_node("cadastro_node", agente_cadastro)

# 2. Criando Nós de Ferramentas SEPARADOS
from langgraph.prebuilt import ToolNode # (caso não tenha importado)

tools_especialista = ToolNode(tools=[consultar_base_de_conhecimento])
tools_cadastro = ToolNode(tools=[cadastrar_cliente])

graph_builder.add_node("tools_especialista", tools_especialista)
graph_builder.add_node("tools_cadastro", tools_cadastro)

# 3. Fluxo de Entrada (Roteamento Inicial)
graph_builder.add_conditional_edges(START, roteador_semantico)

# 4. Fluxos de Saída Direta
graph_builder.add_edge("chat_node", END)

# 5. Fluxo do Agente Especialista
# Usamos um dicionário para mapear a saída da tools_condition (que retorna "tools" por padrão) para o nosso nó personalizado
graph_builder.add_conditional_edges(
    "especialista_node", 
    tools_condition, 
    {"tools": "tools_especialista", END: END}
)
graph_builder.add_edge("tools_especialista", "especialista_node")

# 6. Fluxo do Agente de Cadastro
graph_builder.add_conditional_edges(
    "cadastro_node", 
    tools_condition, 
    {"tools": "tools_cadastro", END: END}
)
graph_builder.add_edge("tools_cadastro", "cadastro_node")
graph_builder.add_edge("cadastro_node", END) 

# Persistência real em SQLite (quando disponível). Se o pacote não estiver
# instalado no ambiente, cai para memória em RAM para não quebrar o boot.
try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore

    conexao_sqlite = sqlite3.connect(
        "memoria_temporaria_langgraph.sqlite", check_same_thread=False
    )
    memory = SqliteSaver(conexao_sqlite)
except ModuleNotFoundError:
    memory = MemorySaver()

app_graph = graph_builder.compile(checkpointer=memory)


def executar_chat(pergunta: str, session_id: str) -> str:
    """
    Encapsula a chamada ao LangGraph, garantindo que o histórico 
    da conversa (memória) seja isolado por session_id.
    """
    # Configura a memória do LangGraph para usar o ID recebido
    config = {"configurable": {"thread_id": session_id}}
    
    # Executa o grafo
    resultado = app_graph.invoke({"messages": [("user", pergunta)]}, config)
    
    # Pega a resposta gerada em formato de texto e retorna
    resposta_final = resultado["messages"][-1].content
    return resposta_final
