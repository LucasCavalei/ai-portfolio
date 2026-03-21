# ARQUIVO: agents/test_sql.py
import os
from typing import Annotated, TypedDict
from flask import Blueprint, request, jsonify
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy import create_engine, text

# 1. Cria o Blueprint em vez do app principal
sql_blueprint = Blueprint('sql', __name__)

# ==========================================
# SETUP DO BANCO E FERRAMENTAS (Mantido igual)
# ==========================================

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/banco_vendas")

# with engine.connect() as conn:
#     conn.execute(text("CREATE TABLE vendas (id INTEGER PRIMARY KEY, produto TEXT, valor REAL, vendedor TEXT);"))
#     conn.execute(text("INSERT INTO vendas (produto, valor, vendedor) VALUES ('Notebook', 4500.0, 'Carlos');"))
#     conn.execute(text("INSERT INTO vendas (produto, valor, vendedor) VALUES ('Mouse', 150.0, 'Ana');"))
#     conn.commit()

@tool
def consultar_banco_de_dados(query: str) -> str:
    """Executa uma query SQL no banco de dados SQLite e retorna o resultado."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            return str(result)
    except Exception as e:
        return f"Erro de sintaxe ou execução no SQL: {e}"

tools = [consultar_banco_de_dados]

# ==========================================
# SETUP DO LLM E LANGGRAPH
# ==========================================
# Como você carregou o load_dotenv() no main.py, a chave da OpenAI já estará disponível aqui!
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,  # Um pouco mais criativo mas ainda consistente
    max_tokens=300,  # Limita o tamanho das respostas
    verbose=False  # Evita o erro do verbose
)
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]

def agente_chatbot(state: State):
    schema = "Tabela vendas: id (INTEGER), produto (TEXT), valor (REAL), vendedor (TEXT)"
    mensagem_sistema = {
        "role": "system", 
        "content": f"Você é um analista de dados. O schema do banco é: {schema}. Gere a query SQL, use a ferramenta e explique o resultado."
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta_ia = llm_with_tools.invoke(mensagens_para_ia)
    return {"messages": [resposta_ia]}

graph_builder = StateGraph(State)
graph_builder.add_node("agente", agente_chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "agente")
graph_builder.add_conditional_edges("agente", tools_condition)
graph_builder.add_edge("tools", "agente")

app_graph = graph_builder.compile()

# ==========================================
# ROTA DO BLUEPRINT
# ==========================================
# Como no main.py você usou url_prefix='/api', essa rota será acessada em /api/chat
@sql_blueprint.route('/sql', methods=["POST"])
def chat_endpoint():
    dados = request.get_json()
    
    if not dados or "pergunta" not in dados:
        return jsonify({"erro": "Envie um JSON com o campo 'pergunta'."}), 400
        
    pergunta = dados["pergunta"]
    estado_inicial = {"messages": [("user", pergunta)]}
    
    # Executa o grafo do LangGraph
    resultado = app_graph.invoke(estado_inicial)
    resposta_final = resultado["messages"][-1].content
    
    return jsonify({"resposta": resposta_final})