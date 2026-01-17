from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq 
from dotenv import load_dotenv

load_dotenv()

CAMINHO_DB = "db"

prompt_template = """ Responda a pergunta do usuario:
{pergunta}

Com base nessas informacoes:

{Base_conhecimento}

Se você não encontrar a resposta para a pergunta do usuario nessas informacoes, responda não sei te dizer isso"""

def perguntar():
    pergunta = input("Escreva sua pergunta: ")
    funcao_embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory=CAMINHO_DB, embedding_function=funcao_embedding)

    resultados = db.similarity_search_with_relevance_scores (pergunta, k=4)
    if len(resultados) == 0 or resultados[0][1] < 0.6:
        print("Nenhum consegiu encontar alguma informação relevante")
        return
    textos_resultados = []
    for resultado in resultados:
       texto = resultado[0].page_content
       textos_resultados.append(texto)

    base_conhecimento = "\n\n------\n\n".join(textos_resultados)
    prompt = ChatPromptTemplate.from_template(prompt_template)
    prompt = prompt.invoke({"pergunta": pergunta, "Base_conhecimento": base_conhecimento})
    print(prompt)
  
    model = ChatGroq(model="llama-3.3-70b-versatile")
    texto_resposta = model.invoke(prompt).content
    print(texto_resposta)
perguntar()