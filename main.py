from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

CAMINHO_DB = "db"

prrompt_template = """ Responda a pergunta do usuario:
{pergunta}

Com base nessas informacoes:

{Ba se_conhecimento}

Se você não encontrar a resposta para a pergunta do usuario nessas informacoes, responda não sei te dizer isso"""

pergunta = input("Escreva sua pergunta: ")

funcao_embedding = HuggingFaceEmbeddings()
db = Chroma(persist_directory=CAMINHO_DB, embedding_function=funcao_embedding)
 