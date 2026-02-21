from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.document_loaders import TextLoader 
from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereEmbeddings
from pinecone import Pinecone
import os

from main import PINECONE_INDEX_NAME

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") 

PASTA_BASE = "base"

def load_documents(): 
    # Carrega arquivos PDF
    pdf_loader = PyPDFDirectoryLoader(PASTA_BASE, glob="**/*.pdf")
    pdf_documents = pdf_loader.load()
    
    # Carrega arquivos Markdown (.md)
    md_loader = DirectoryLoader(
        PASTA_BASE, 
        glob="**/*.md", 
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    md_documents = md_loader.load()
    
    # Combina todos os documentos
    todos_documentos = pdf_documents + md_documents
    print(f"Carregados {len(pdf_documents)} PDFs e {len(md_documents)} arquivos Markdown")
    print(f"Total de documentos: {len(todos_documentos)}")
    
    return todos_documentos

def dividir_chunks(documents):
    separador_documentos = RecursiveCharacterTextSplitter(
        chunk_size=2000,    
        chunk_overlap=500,
        length_function=len,
        add_start_index=True     )
    chunks = separador_documentos.split_documents(documents)
    print(f"Total de chunks criados: {len(chunks)}")
    return chunks

def vetorizar_chunks(chunks):
#     db = Chroma.from_documents(
#         documents=chunks, 
#         embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
#         persist_directory="./db" 
#     )
#     print("DB criado e salvo com sucesso na pasta 'db'")
    
    #Agora usamos Cohere para vetorizar / criar os embeddings
    funcao_embedding = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY")
    )
    print("Iniciando upload para o Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    # 2 - Esta linha que faz o  restante com os chunks
    PineconeVectorStore.from_documents(
        documents=chunks, 
        embedding=funcao_embedding,
        index_name=PINECONE_INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY
    )
    print(f"Sucesso! Todos os dados foram enviados para o índice '{PINECONE_INDEX_NAME}' na nuvem.")

def create_db(): 
    documents = load_documents()
    if not documents:
        print("Nenhum documento encontrado na pasta.")
        return
    chunks = dividir_chunks(documents)
    vetorizar_chunks(chunks)

if __name__ == "__main__":
    create_db()
