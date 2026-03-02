# ARQUIVO: src/agents/bot_lucas.py

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Importa a função de busca do banco de dados vetorial
from database.vector_db import buscar_contexto

# 1. Template Customizado - Melhorado para respostas mais naturais
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
8. Use acentuação corretamente (á, é, í, ó, ú, ç, ã, õ)

Exemplos de como responder:
Pergunta: "Quem é Lucas?"
Resposta: "Lucas é um desenvolvedor de software focado em tecnologias modernas. Quer saber mais sobre alguma área específica dele, como experiências ou projetos?"

Pergunta: "Quais projetos ele fez?"
Resposta: "Ele trabalhou em alguns projetos interessantes na área de desenvolvimento. Tem algum tipo de projeto específico que você gostaria de saber mais?"

Pergunta: "Onde ele estudou?"
Resposta: "Lucas tem formação na área de tecnologia. Quer saber mais sobre sua formação acadêmica ou cursos específicos?"
"""

# Configuração do modelo com parâmetros otimizados
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,  # Um pouco mais criativo mas ainda consistente
    max_tokens=300,  # Limita o tamanho das respostas
)

# 3. Gerenciamento de Memória
store = {}

def get_session_history(session_id: str):
    """Retorna o histórico de conversas de uma sessão"""
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
    """Função principal que executa o chat sobre Lucas Rodrigues"""
    try:
        # ID da sessão (Poderia ser dinâmico no futuro)
        config = {"configurable": {"session_id": "usuario_teste_123"}}

        # Busca o contexto no banco de dados isolado
        base_conhecimento = buscar_contexto(pergunta)

        # Execução com Histórico
        resposta = with_message_history.invoke(
            {
                "pergunta": pergunta, 
                "Base_conhecimento": base_conhecimento
            },
            config=config
        )

        # Limpa e retorna a resposta
        resposta_limpa = resposta.content.strip()
        
        # Garante que a resposta não seja muito longa
        if len(resposta_limpa) > 500:
            resposta_limpa = resposta_limpa[:500] + "..."
            
        return resposta_limpa
        
    except Exception as e:
        return f"Desculpe, tive um problema ao processar sua pergunta. Pode tentar novamente? Erro: {str(e)}"