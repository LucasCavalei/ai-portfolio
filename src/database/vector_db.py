import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Configuração do Vector Database
def get_vector_db():
    """Retorna a conexão com o Pinecone Vector Store"""
    funcao_embedding = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY")
    )
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    vector_db = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME, 
        embedding=funcao_embedding, 
        pinecone_api_key=PINECONE_API_KEY
    )
    
    return vector_db

# Função para buscar documentos relevantes (nome correto para o import)
def buscar_contexto(query, k=4, threshold=0.3):
    """Busca documentos relevantes na base de conhecimento"""
    vector_db = get_vector_db()
    resultados = vector_db.similarity_search_with_relevance_scores(query, k=k)
    
    if len(resultados) == 0 or resultados[0][1] < threshold:
        return "Nenhuma informação relevante encontrada no banco de dados."
    else:
        textos_resultados = [res[0].page_content for res in resultados]
        return "\n\n-----------------\n\n".join(textos_resultados)