"""Vector store — semantic memory using Qdrant + sentence-transformers."""

from typing import Any
from .config import (
    QDRANT_URL, QDRANT_API_KEY,
    COLLECTION_MEMORY, COLLECTION_INVENTORY, COLLECTION_EPISODES,
    EMBEDDING_MODEL, EMBEDDING_DIM, MAX_CONTEXT_FACTS
)


def _get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


_embedder = None

def embed(text: str) -> list[float]:
    global _embedder
    if _embedder is None:
        _embedder = _get_embedder()
    return _embedder.encode(text).tolist()


def init_collections():
    """Create Qdrant collections if they don't exist."""
    from qdrant_client.models import VectorParams, Distance
    client = _get_client()

    for name in [COLLECTION_MEMORY, COLLECTION_INVENTORY, COLLECTION_EPISODES]:
        existing = [c.name for c in client.get_collections().collections]
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )
            print(f"Created Qdrant collection: {name}")


def store_fact(text: str, metadata: dict, collection: str = COLLECTION_MEMORY) -> str:
    """Store a fact in the vector store. Returns the point ID."""
    import uuid
    from qdrant_client.models import PointStruct

    client = _get_client()
    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=collection,
        points=[PointStruct(
            id=point_id,
            vector=embed(text),
            payload={"text": text, **metadata}
        )]
    )
    return point_id


def retrieve(query: str, collection: str = COLLECTION_MEMORY,
             limit: int = MAX_CONTEXT_FACTS) -> list[dict]:
    """Retrieve the most relevant facts for a query."""
    client = _get_client()
    results = client.search(
        collection_name=collection,
        query_vector=embed(query),
        limit=limit,
        with_payload=True
    )
    return [{"text": r.payload["text"], "score": r.score, **r.payload}
            for r in results]


def retrieve_all(query: str, limit: int = MAX_CONTEXT_FACTS) -> list[dict]:
    """Search across memory + inventory + episodes."""
    results = []
    for collection in [COLLECTION_MEMORY, COLLECTION_INVENTORY, COLLECTION_EPISODES]:
        try:
            hits = retrieve(query, collection=collection, limit=limit // 3)
            for h in hits:
                h["collection"] = collection
            results.extend(hits)
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
