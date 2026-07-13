"""Recuperación de fragmentos de políticas (vectorial + keywords)."""
import math
import re
from pathlib import Path
from typing import Any

from app.rag.ingest import CACHE_FILE, chunk_documents, generate_embedding, load_local_cache, save_local_cache

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
    chunks = chunk_documents()
    enriched = [{**c, "embedding": generate_embedding(c["content"])} for c in chunks]
    save_local_cache(enriched)
    return enriched


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


def retrieve_policy_chunks(query: str, limit: int = 3, min_score: float = MIN_SCORE) -> list[dict]:
    """Búsqueda semántica local con fallback por palabras clave."""
    if not _meaningful_query(query):
        return []
    query_embedding = generate_embedding(query)
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
    results = [item[1] for item in scored[:limit]]

    if not results:
        results = _keyword_search(query, limit)

    return results
