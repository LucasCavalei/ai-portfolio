"""
Roteamento de intenção por embeddings (item 4 — similaridade vetorial).

Para cada intenção guardamos várias frases-âncora em PT-BR; calculamos o centróide
(média dos vetores) por intenção. A mensagem do usuário vira embedding; comparamos
cosseno com cada centróide e escolhemos a intenção com maior score, se >= limiar.

Requisito: COHERE_API_KEY (mesmo modelo que src/database/vector_db.py).
Se indisponível ou score abaixo do limiar, retorna None e o nodes.roteador_semantico
usa o fallback llm_roteador (Groq + structured output Rota), como antes.
"""
from __future__ import annotations

import math
import os
from typing import Dict, List, Literal, Optional

from dotenv import load_dotenv

load_dotenv()

Destino = Literal["chat_node", "especialista_node", "cadastro_node"]

# Frases-âncora por intenção (ajuste conforme o tom do produto).
ANCHORS: Dict[str, List[str]] = {
    "cadastro_node": [
        "quero me cadastrar",
        "me cadastra por favor",
        "preciso deixar meu contato",
        "quero registrar meus dados",
        "meu cpf é",
        "meu telefone é",
        "como faço para me cadastrar",
        "gostaria de ser lead",
        "enviar meus dados pessoais",
    ],
    "especialista_node": [
        "quem é o Lucas Rodrigues",
        "quais projetos o Lucas fez",
        "onde o Lucas trabalhou",
        "formação acadêmica do Lucas",
        "experiência profissional Lucas",
        "fale sobre o currículo do Lucas",
        "o que o Lucas desenvolve",
        "stack tecnológica do Lucas",
    ],
    "chat_node": [
        "oi tudo bem",
        "bom dia",
        "obrigado pela ajuda",
        "como você pode me ajudar",
        "até logo",
        "beleza valeu",
        "só puxando assunto",
        "conversa casual",
    ],
}

_centroids: Optional[Dict[str, List[float]]] = None
_embedder = None


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _mean_vec(vectors: List[List[float]]) -> List[float]:
    if not vectors:
        return []
    d = len(vectors[0])
    n = len(vectors)
    return [sum(vectors[i][j] for i in range(n)) / n for j in range(d)]


def _get_embedder():
    global _embedder
    if _embedder is not None:
        return _embedder
    if not os.getenv("COHERE_API_KEY"):
        return None
    from langchain_cohere import CohereEmbeddings

    _embedder = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY"),
    )
    return _embedder


def _build_centroids() -> Optional[Dict[str, List[float]]]:
    emb = _get_embedder()
    if emb is None:
        return None
    out: Dict[str, List[float]] = {}
    for intent, phrases in ANCHORS.items():
        vecs = [emb.embed_query(p) for p in phrases]
        out[intent] = _mean_vec(vecs)
    return out


def classificar_por_embedding(texto: str) -> Optional[Destino]:
    """
    Retorna um dos três nós se a similaridade máxima >= limiar; senão None (usar LLM).
    Desligar: ROUTER_EMBEDDING_ENABLED=0
    Limiar: ROUTER_EMBEDDING_THRESHOLD (default 0.32; subir se houver falsos positivos).
    """
    if os.getenv("ROUTER_EMBEDDING_ENABLED", "1").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        return None
    texto = (texto or "").strip()
    if not texto:
        return None

    global _centroids
    if _centroids is None:
        _centroids = _build_centroids()
    if not _centroids:
        return None

    emb = _get_embedder()
    if emb is None:
        return None

    q = emb.embed_query(texto)
    best: Optional[Destino] = None
    best_score = -1.0
    for intent, centroid in _centroids.items():
        s = _cosine(q, centroid)
        if s > best_score:
            best_score = s
            best = intent  # type: ignore[assignment]

    try:
        thresh = float(os.getenv("ROUTER_EMBEDDING_THRESHOLD", "0.32"))
    except ValueError:
        thresh = 0.32

    if best is None or best_score < thresh:
        return None
    return best
    """PGVECTOR X EMBEDDING_ROUTER(esse nosso)"""
    # PGVECTOR:
    # - Guarda muitos vetores (trechos de texto, linhas de tabela)
    # - Faz uma busca dos vizinhos mais próximos ao vetor da pergunta
    # - Isso é o que as pessoas costumam chamar de busca semântica em RAG: “documentos cujo significado está perto da query”.
    # EMBEDDING_ROUTER:
    # - Também transforma texto em vetor, mas não está procurando em milhares de documentos.
    # - Está comparando o vetor da mensagem do usuário com poucos vetores fixos (os centróides das intenções: cadastro / especialista / chat).
    # - Ou seja: é classificação por similaridade, não recuperação de base de conhecimento.


