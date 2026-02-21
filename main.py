import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# 1. Template Customizado para responder sobre Lucas Cavalcante
prompt_template = """Você é um assistente amigável que conversa sobre Lucas Rodrigues, desenvolvedor de software. 
Use a base de conhecimento para responder de forma natural e conversada, como se estivesse numa conversa real.

Base de Conhecimento sobre Lucas:
{Base_conhecimento}

Histórico da Conversa:
{history}

Pergunta do Usuário: 
{pergunta}

Instruções importantes:
1. Responda de forma CONVERSADA e NATURAL, não como um robô
2. Dê informações de forma GRADUAL - não junte tudo de uma vez
3. Se perguntarem "quem é Lucas", dê uma introdução breve e sugira perguntas específicas
4. Use frases como "Sobre isso...", "Ah, sim...", "Posso te contar que..." para soar mais humano
5. Responda apenas ao que foi perguntado, não adicione informações extras não solicitadas
6. Seja breve e direto nas respostas (2-3 frases no máximo)
7. Se não tiver a informação, diga "Sobre isso não tenho detalhes específicos, mas posso te ajudar com outras coisas sobre o trabalho dele"

Exemplo de como responder:
Pergunta: "Quem é Lucas?"
Resposta: "Lucas é um desenvolvedor de software focado em tecnologias modernas. Quer saber mais sobre alguma área específica dele, como experiências ou projetos?"

Pergunta: "Quais projetos ele fez?"
Resposta: "Ele trabalhou em alguns projetos interessantes na área de desenvolvimento. Tem algum tipo de projeto específico que você gostaria de saber mais?"""

# 2. Configuração Global (usando APIs na nuvem)
funcao_embedding = CohereEmbeddings(
    model="embed-multilingual-v3.0",
    cohere_api_key=os.getenv("COHERE_API_KEY")
)
pc = Pinecone(api_key=PINECONE_API_KEY)
vector_db = PineconeVectorStore(index_name=PINECONE_INDEX_NAME, embedding=funcao_embedding, pinecone_api_key=PINECONE_API_KEY)

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

def executar_chat(pergunta):
    # ID da sessão (Poderia ser o ID do usuário vindo do WhatsApp ou Chat)
    config = {"configurable": {"session_id": "usuario_teste_123"}}
    
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

    return resposta.content
