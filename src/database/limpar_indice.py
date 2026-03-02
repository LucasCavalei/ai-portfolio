from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)

print(f"🧹 Limpando índice '{PINECONE_INDEX_NAME}'...")

# Deletar todos os dados do índice
index = pc.Index(PINECONE_INDEX_NAME)
index.delete(delete_all=True)

print("✅ Índice limpo com sucesso!")
print("🚀 Agora execute 'python create_db.py' para carregar seus dados sobre você")
