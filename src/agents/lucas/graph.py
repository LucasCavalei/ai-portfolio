import sqlite3
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .nodes import (
    agente_bate_papo,
    agente_cadastro,
    agente_especialista,
    roteador_semantico,
)
from .state import State
from .tools import cadastrar_cliente, consultar_base_de_conhecimento

# ==========================================
# 5. CONSTRUÇÃO DO GRAFO (Arquitetura)
# ==========================================
graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", agente_bate_papo)
graph_builder.add_node("especialista_node", agente_especialista)
graph_builder.add_node("cadastro_node", agente_cadastro)

tools_especialista = ToolNode(tools=[consultar_base_de_conhecimento])
tools_cadastro = ToolNode(tools=[cadastrar_cliente])

graph_builder.add_node("tools_especialista", tools_especialista)
graph_builder.add_node("tools_cadastro", tools_cadastro)

graph_builder.add_conditional_edges(START, roteador_semantico)

graph_builder.add_edge("chat_node", END)

graph_builder.add_conditional_edges(
    "especialista_node",
    tools_condition,
    {"tools": "tools_especialista", END: END},
)
graph_builder.add_edge("tools_especialista", "especialista_node")

graph_builder.add_conditional_edges(
    "cadastro_node",
    tools_condition,
    {"tools": "tools_cadastro", END: END},
)
graph_builder.add_edge("tools_cadastro", "cadastro_node")
graph_builder.add_edge("cadastro_node", END)

# Caminho fixo ao lado deste módulo (não depende do cwd do processo Flask).
_SQLITE_PATH = Path(__file__).resolve().parent / "memoria_temporaria_langgraph.sqlite"
memory = MemorySaver()
try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore

    conexao_sqlite = sqlite3.connect(
        str(_SQLITE_PATH),
        check_same_thread=False,
        timeout=30.0,
    )
    memory = SqliteSaver(conexao_sqlite)
except Exception:
    memory = MemorySaver()

app_graph = graph_builder.compile(checkpointer=memory)


def _ultima_resposta_como_texto(msgs: list) -> str:
    """Groq/LangChain podem devolver content str ou lista de blocos; o JSON do Flask exige string."""
    if not msgs:
        return ""
    raw = getattr(msgs[-1], "content", None)
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return " ".join(parts).strip()
    return str(raw).strip()


def executar_chat(
    pergunta: str,
    session_id: str,
    topico: str | None = None,
    idioma: str | None = None,
) -> str:
    """
    Encapsula a chamada ao LangGraph, garantindo que o histórico
    da conversa (memória) seja isolado por session_id.
    topico: "whamais" | "lucas" — define o foco do assistente.
    idioma: "pt" | "en" — idioma das respostas do assistente.
    """
    config = {"configurable": {"thread_id": session_id}}
    payload: dict = {"messages": [("user", pergunta)]}
    if topico in ("whamais", "lucas"):
        payload["topico"] = topico
    if idioma in ("pt", "en"):
        payload["idioma"] = idioma
    resultado = app_graph.invoke(payload, config)
    return _ultima_resposta_como_texto(resultado.get("messages") or [])
