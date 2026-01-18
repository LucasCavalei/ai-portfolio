import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

CAMINHO_DB = "db"

# 1. Seu Template Customizado com a variável {history} adicionada
prompt_template = """Você é um assistente de suporte técnico especializado. 
Use os seguintes fragmentos de documentação para responder à dúvida do usuário, , porém fique a vontade para ser habilidosa sociavel.

Documentação Relevante:
{Base_conhecimento}

Histórico da Conversa:
{history}

Dúvida do Usuário: 
{pergunta}

Instruções:
1. Responda de forma clara e profissional.
2. Se a solução não estiver presente na "Documentação Relevante" acima, 
   responda exatamente: "Desculpe, não encontrei informações suficientes nos manuais para resolver este problema."
3. Pode ser habilidosa sociavel."""

# 2. Configuração Global (fora da função para não recarregar toda hora)
funcao_embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory=CAMINHO_DB, embedding_function=funcao_embedding)
model = ChatGroq(model="llama-3.3-70b-versatile")

# 3. Gerenciamento de Memória
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 4. Criação da Chain com Histórico
prompt = PromptTemplate.from_template(prompt_template)
chain = prompt | model

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="pergunta",
    history_messages_key="history",
)

def perguntar():
    # ID da sessão (Poderia ser o ID do usuário vindo do WhatsApp ou Chat)
    config = {"configurable": {"session_id": "usuario_teste_123"}}
    
    while True:
        pergunta = input("\nEscreva sua pergunta (ou 'sair'): ")
        if pergunta.lower() == 'sair':
            break

        # BUSCA NO RAG (Igual ao seu código original)
        resultados = vector_db.similarity_search_with_relevance_scores(pergunta, k=4)
        
        if len(resultados) == 0 or resultados[0][1] < 0.3: # Ajustei o threshold para 0.3
            base_conhecimento = "Nenhuma informação relevante encontrada no banco de dados."
        else:
            textos_resultados = [res[0].page_content for res in resultados]
            base_conhecimento = "\n\n-----------------\n\n".join(textos_resultados)

        # EXECUÇÃO COM HISTÓRICO
        # O 'with_message_history' injeta automaticamente o histórico na variável {history}
        resposta = with_message_history.invoke(
            {
                "pergunta": pergunta, 
                "Base_conhecimento": base_conhecimento
            },
            config=config
        )

        print("\nBot:", resposta.content)

if __name__ == "__main__":
    perguntar()