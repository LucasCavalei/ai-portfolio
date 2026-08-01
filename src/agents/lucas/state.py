from typing import Annotated, TypedDict, Literal, Optional, NotRequired
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from .tools import tools

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
    nome: NotRequired[Optional[str]]
    cpf: NotRequired[Optional[str]]
    telefone: NotRequired[Optional[str]]
    em_cadastro: NotRequired[Optional[bool]]
    topico: NotRequired[Optional[str]]  # "whamais" | "lucas"
    idioma: NotRequired[Optional[str]]  # "pt" | "en"

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
            "2. 'especialista_node': Se o usuário pedir informações sobre a Whamais (empresa, soluções IA, WhatsApp, voz, agenda) "
            "ou sobre Lucas Rodrigues (fundador, carreira, projetos, formação, experiência). "
            "3. 'chat_node': Para saudações, conversas gerais ou qualquer assunto que não se encaixe nos anteriores."
        )
    )

# Usado como fallback quando classificar_por_embedding (embedding_router) retorna None.
llm_roteador = llm.with_structured_output(Rota)
