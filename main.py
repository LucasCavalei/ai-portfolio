from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
# 2. Inicialize o modelo
# Modelos populares: "llama-3.3-70b-versatile" ou "mixtral-8x7b-32768"
chat = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=groq_api_key
)

# 3. Lista para armazenar o histórico da conversa
historico = [
    SystemMessage(content="Você é um assistente prestativo e responde em português.")
]

print("--- Chatbot Groq + LangChain (digite 'sair' para encerrar) ---")

while True:
    pergunta_usuario = input("\nVocê: ")
    
    if pergunta_usuario.lower() in ["sair", "exit", "quit"]:
        break

    # Adiciona a pergunta do usuário ao histórico
    historico.append(HumanMessage(content=pergunta_usuario))

    # Chama o modelo passando todo o histórico
    resposta = chat.invoke(historico)
    
    # Exibe a resposta e guarda no histórico para o bot ter contexto
    print(f"Bot: {resposta.content}")
    historico.append(AIMessage(content=str(resposta.content)))