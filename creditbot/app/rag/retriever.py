"""Recuperación de fragmentos de políticas (pgvector + local + keywords)."""
import math
import re
from typing import Any

from app.core.config import settings
from app.rag.ingest import chunk_documents, generate_embedding, load_local_cache, save_local_cache

MIN_SCORE = 0.35


def _meaningful_query(query: str) -> bool:
    """Filtra consultas demasiado cortas o sin términos útiles."""
    terms = [t for t in re.findall(r"[a-záéíóúñ]+", query.lower()) if len(t) >= 4]
    return len(terms) > 0


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _ensure_cache() -> list[dict[str, Any]]:
    cached = load_local_cache()
    if cached:
        return cached
    from app.rag.ingest import chunk_documents as cd, generate_embedding as ge

    chunks = cd()
    enriched = [{**c, "embedding": ge(c["content"])} for c in chunks]
    save_local_cache(enriched)
    return enriched


def _search_supabase(query_embedding: list[float], limit: int, min_score: float) -> list[dict]:
    """Búsqueda vectorial en pgvector vía RPC."""
    if len(query_embedding) != 1536 or not settings.supabase_url:
        return []
    try:
        from app.repositories.supabase_client import get_supabase_client

        response = get_supabase_client().rpc(
            "match_rag_chunks",
            {
                "query_embedding": query_embedding,
                "match_threshold": min_score,
                "match_count": limit,
            },
        ).execute()
        results = []
        for row in response.data or []:
            results.append(
                {
                    "content": row["content"],
                    "source": row.get("source_path") or "supabase",
                    "title": row.get("title") or "",
                    "score": round(float(row.get("similarity", 0)), 3),
                    "method": "pgvector",
                }
            )
        return results
    except Exception:
        return []


def _keyword_search(query: str, limit: int) -> list[dict[str, Any]]:
    query_terms = {t.lower() for t in query.split() if len(t) > 3}
    if not query_terms:
        return []

    scored: list[tuple[float, dict]] = []
    for chunk in chunk_documents():
        text_lower = chunk["content"].lower()
        matches = sum(1 for term in query_terms if term in text_lower)
        if matches:
            score = matches / len(query_terms)
            scored.append((score, {**chunk, "score": round(score, 2), "method": "keyword"}))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def _search_local(query_embedding: list[float], limit: int, min_score: float) -> list[dict]:
    cache = _ensure_cache()
    scored: list[tuple[float, dict]] = []
    for chunk in cache:
        embedding = chunk.get("embedding", [])
        score = _cosine_similarity(query_embedding, embedding)
        if score >= min_score:
            scored.append(
                (
                    score,
                    {
                        "content": chunk["content"],
                        "source": chunk["source"],
                        "title": chunk["title"],
                        "score": round(score, 3),
                        "method": "vector",
                    },
                )
            )
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def retrieve_policy_chunks(query: str, limit: int = 3, min_score: float = MIN_SCORE) -> list[dict]:
    """Búsqueda semántica con pgvector, caché local y keywords."""
    if not _meaningful_query(query):
        return []

    query_embedding = generate_embedding(query)
    results = _search_supabase(query_embedding, limit, min_score)

    if not results and len(query_embedding) != 1536:
        results = _search_local(query_embedding, limit, min_score)
    elif not results:
        pseudo = generate_embedding(query)
        results = _search_local(pseudo, limit, min_score)

    if not results:
        results = _keyword_search(query, limit)

    return results
