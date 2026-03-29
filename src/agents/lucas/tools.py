import os
import uuid
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, text
from langchain_core.tools import tool
from database.vector_db import buscar_contexto

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
