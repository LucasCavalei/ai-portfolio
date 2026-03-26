import os
import uuid
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Literal,Optional
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import create_engine, text
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

load_dotenv()

# Pega exatamente a variável que você criou no .env (opcional: sem isso o cadastro fica desativado)
DATABASE_URL = os.getenv("ZAP_DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None


@tool
def cadastrar_cliente(telefone: str, nome: str = None, cpf: str = None) -> str:
    """
    Cadastra um novo cliente no banco de dados para o fluxo do chatbot.
    Recebe o telefone (obrigatório), nome e CPF (opcionais).
    """
    if engine is None:
        return "Cadastro indisponível no momento (banco de dados não configurado)."

    # Gerar um UUID único para o novo cliente
    novo_id = str(uuid.uuid4())
    
    query = text("""
        INSERT INTO clientes (id, telefone_whatsapp, nome, cpf, fase_funil, ultima_interacao)
        VALUES (:id, :tel, :nome, :cpf, 'Novo Lead', :agora)
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "id": novo_id,
                "tel": telefone,
                "nome": nome,
                "cpf": cpf,
                "agora": datetime.now()
            })
            conn.commit()
            return f"Cliente {nome or telefone} cadastrado com sucesso! ID: {novo_id}"
            
    except Exception as e:
        if "Duplicate entry" in str(e):
            return "Erro: Este número de WhatsApp já está cadastrado."
        return f"Erro ao cadastrar cliente: {e}"
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


# Atualizando sua lista de tools
tools = [cadastrar_cliente,consultar_base_de_conhecimento]
# ==========================================
# 2. SETUP DO LLM E ESTRUTURAS DE DADOS
# ==========================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3, 
    max_tokens=300,
    verbose=False
)

llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

# ==========================================
# 3. O ROTEADOR INTELIGENTE (Intent Routing)
# ==========================================
class DadosCliente(BaseModel):
    nome: Optional[str] = Field(None, description="Nome completo do usuário")
    telefone: Optional[str] = Field(None, description="Número do WhatsApp")
    cpf: Optional[str] = Field(None, description="CPF do usuário")

class Rota(BaseModel):
    destino: Literal["chat_node", "especialista_node", "cadastro_node"] = Field(
        description=(
            "Decida o próximo nó com base na intenção do usuário: "
            "1. 'cadastro_node': Se o usuário fornecer dados pessoais (nome, CPF, telefone) ou demonstrar interesse em se cadastrar/deixar contato. "
            "2. 'especialista_node': Se o usuário pedir informações específicas sobre Lucas (quem ele é, projetos, formação ou experiência). "
            "3. 'chat_node': Para saudações, conversas gerais ou qualquer assunto que não se encaixe nos anteriores."
        )
    )

llm_roteador = llm.with_structured_output(Rota)

def agente_cadastro(state: State):
    # 1. Resgatamos o que o LangGraph já memorizou nas rodadas anteriores
    nome_salvo = state.get("nome")
    cpf_salvo = state.get("cpf")
    telefone_salvo = state.get("telefone")

    # Pegamos APENAS a última mensagem digitada pelo usuário
    ultima_msg = state["messages"][-1].content

    # 2. Configura o LLM extrator usando a sua classe
    llm_extrator = llm.with_structured_output(DadosCliente)
    
    # O prompt agora é simples e direto para analisar apenas a última fala
    dados_extraidos = llm_extrator.invoke(
        f"Extraia nome, cpf ou telefone do seguinte texto (retorne null para o que não achar): '{ultima_msg}'"
    )
    
    # 3. Atualizamos a nossa "memória" se a IA tiver achado algo novo agora
    if dados_extraidos.nome: nome_salvo = dados_extraidos.nome
    if dados_extraidos.cpf: cpf_salvo = dados_extraidos.cpf
    if dados_extraidos.telefone: telefone_salvo = dados_extraidos.telefone

    # ==========================================
    # 4. Lógica de Feedback e Roteamento (SUA LÓGICA MANTIDA)
    # ==========================================
    
    # Cenário A: Falta o Nome
    if not nome_salvo:
        # Verifica se ele já mandou o CPF logo de cara
        if cpf_salvo:
            msg = "Anotei o seu CPF. Qual o seu nome completo?"
        # Verifica se ele mandou o telefone primeiro
        elif telefone_salvo:
            msg = "Anotei o seu telefone. Para continuarmos, qual o seu nome completo?"
        # Não mandou nada ainda
        else:
            msg = "Olá! Para começarmos o seu cadastro, qual é o seu nome completo?"
            
        # IMPORTANTE: Além da mensagem, retornamos os dados para o LangGraph guardar!
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # Cenário B: Temos o Nome, mas falta o CPF
    if not cpf_salvo:
        msg = f"Prazer, {nome_salvo}! Agora só preciso do seu CPF."
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # Cenário C: Temos Nome e CPF, mas falta o Telefone
    if not telefone_salvo:
        msg = f"Certo, {nome_salvo}! Já anotei seu CPF. Por fim, qual o seu telefone com DDD?"
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # ==========================================
    # 5. Todos os dados preenchidos! Chama a Tool
    # ==========================================
    try:
        # Executa a tool do Langchain com as variáveis consolidadas
        resultado_tool = cadastrar_cliente.invoke({
            "nome": nome_salvo, 
            "cpf": cpf_salvo, 
            "telefone": telefone_salvo
        })
        
        mensagem_final = f"Pronto, {nome_salvo}! Seu cadastro foi finalizado com sucesso."
        return {
            "messages": [("assistant", mensagem_final)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }
        
    except Exception as e:
        return {
            "messages": [("assistant", f"Ops, ocorreu um erro ao salvar: {e}")],
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }
def roteador_semantico(state: State) -> Literal["chat_node", "especialista_node", "cadastro_node"]:
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