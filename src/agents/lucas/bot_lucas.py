import os
import uuid
from typing import Annotated, TypedDict, Literal
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from database.vector_db import buscar_contexto





# Mudei o nome do blueprint para fazer mais sentido, mas a estrutura do Flask é a mesma
portfolio_blueprint = Blueprint('portfolio', __name__)

# ==========================================
# 1. SETUP DA BASE E FERRAMENTAS
# ==========================================
# Substituímos o banco SQL por uma base de texto para a IA consultar usando a mesma mecânica de Tool

@tool
def consultar_base_de_conhecimento(query: str) -> str:
    """Busca informações na base de conhecimento sobre as experiências, formação e projetos de Lucas Rodrigues."""
    
    # A IA vai inventar a 'query' sozinha baseada na pergunta do usuário.
    # Ex: O usuário digita "Onde o Lucas trabalhou?", a IA manda query="experiência profissional".
    
    try:
        base_conhecimento = buscar_contexto(query)
        return base_conhecimento
    except Exception as e:
        print(f"Erro ao consultar o Pinecone: {e}")
        return "Desculpe, no momento não consegui acessar os detalhes do meu currículo."

tools = [consultar_base_de_conhecimento]

# ==========================================
# 2. SETUP DO LLM E ESTRUTURAS DE DADOS
# ==========================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3, 
    max_tokens=500,
    verbose=False
)

# O LLM com as ferramentas acopladas (usado APENAS pelo especialista)
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

# ==========================================
# 3. O ROTEADOR INTELIGENTE (Intent Routing)
# ==========================================
class Rota(BaseModel):
    # Alteramos o Literal para refletir os novos nós
    destino: Literal["chat_node", "especialista_node"] = Field(
        description="Escolha 'especialista_node' APENAS se o usuário pedir informações sobre Lucas, quem ele é, seus projetos, formação ou experiência. Escolha 'chat_node' para saudações (oi, tudo bem) ou conversas gerais."
    )

llm_roteador = llm.with_structured_output(Rota)

def roteador_semantico(state: State) -> Literal["chat_node", "especialista_node"]:
    """Analisa a última mensagem e decide para qual especialista enviar."""
    ultima_mensagem = state["messages"][-1].content
    try:
        decisao = llm_roteador.invoke(ultima_mensagem)
        return decisao.destino
    except Exception as e:
        print(f"Erro ao falar com a Groq no roteador: {e}")
        return "chat_node"

# ==========================================
# 4. OS NÓS ESPECIALISTAS (Personas)
# ==========================================
def agente_bate_papo(state: State):
    """Especialista em interações humanas. Não tem acesso a ferramentas."""
    mensagem_sistema = {
        "role": "system", 
        "content": (
            "Você é um assistente amigável do portfólio de Lucas Rodrigues. "
            "Sua postura é profissional e prestativa. "
            "O usuário está apenas puxando assunto ou te cumprimentando. "
            "Responda de forma breve, educada e natural. "
            "Se perguntarem o que você faz, diga que ajuda a responder perguntas sobre a carreira e os projetos do Lucas."
        )
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta = llm.invoke(mensagens_para_ia)
    return {"messages": [resposta]}

def agente_especialista(state: State):
    """Especialista sobre o Lucas. Tem acesso à base de conhecimento (tool)."""
    # Inserido EXATAMENTE o seu prompt aqui
    mensagem_sistema = {
        "role": "system", 
        "content": (
            "Você é um assistente amigável que conversa sobre Lucas Rodrigues, desenvolvedor de software. "
            "Use a ferramenta 'consultar_base_de_conhecimento' para buscar informações e responder de forma natural e conversada, como se estivesse numa conversa real.\n\n"
            "Instruções importantes:\n"
            "1. Responda de forma CONVERSADA e NATURAL, não como um robô\n"
            "2. Dê informações de forma GRADUAL - não junte tudo de uma vez\n"
            "3. Se perguntarem 'quem é Lucas', dê uma introdução breve e sugira perguntas específicas\n"
            "4. Use frases como 'Sobre isso...', 'Ah, sim...', 'Posso te contar que...' para soar mais humano\n"
            "5. Responda apenas ao que foi perguntado, não adicione informações extras não solicitadas\n"
            "6. Seja breve e direto nas respostas (2-3 frases no máximo)\n"
            "7. Se não tiver a informação, diga 'Sobre isso não tenho detalhes específicos, mas posso te ajudar com outras coisas sobre o trabalho dele'\n"
            "8. Use acentuação corretamente (á, é, í, ó, ú, ç, ã, õ)\n\n"
            "Exemplos de como responder:\n"
            "Pergunta: 'Quem é Lucas?'\n"
            "Resposta: 'Lucas é um desenvolvedor de software focado em tecnologias modernas. Quer saber mais sobre alguma área específica dele, como experiências ou projetos?'\n\n"
            "Pergunta: 'Quais projetos ele fez?'\n"
            "Resposta: 'Ele trabalhou em alguns projetos interessantes na área de desenvolvimento. Tem algum tipo de projeto específico que você gostaria de saber mais?'\n\n"
            "Pergunta: 'Onde ele estudou?'\n"
            "Resposta: 'Lucas tem formação na área de tecnologia. Quer saber mais sobre sua formação acadêmica ou cursos específicos?'"
        )
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta_ia = llm_with_tools.invoke(mensagens_para_ia)
    return {"messages": [resposta_ia]}

# ==========================================
# 5. CONSTRUÇÃO DO GRAFO (Arquitetura)
# ==========================================
graph_builder = StateGraph(State)

# Adicionando os nós (Mudamos 'sql_node' para 'especialista_node')
graph_builder.add_node("chat_node", agente_bate_papo)
graph_builder.add_node("especialista_node", agente_especialista)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Fluxo de Roteamento
graph_builder.add_conditional_edges(START, roteador_semantico)

# Fluxo do Chat Comum
graph_builder.add_edge("chat_node", END)

# Fluxo do Agente Especialista (O loop com as ferramentas)
graph_builder.add_conditional_edges("especialista_node", tools_condition)
graph_builder.add_edge("tools", "especialista_node")

# Compilando com Memória
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