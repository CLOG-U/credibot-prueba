"""Recuperación de fragmentos de políticas (RAG simplificado)."""
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"

_chunk_cache: list[dict[str, str]] | None = None


def _load_chunks() -> list[dict[str, str]]:
    """Carga y trocea documentos markdown locales."""
    global _chunk_cache
    if _chunk_cache is not None:
        return _chunk_cache

    chunks: list[dict[str, str]] = []
    for doc_path in DOCUMENTS_DIR.glob("*.md"):
        content = doc_path.read_text(encoding="utf-8")
        sections = [s.strip() for s in content.split("\n## ") if s.strip()]
        for i, section in enumerate(sections):
            if i > 0:
                section = "## " + section
            chunks.append(
                {
                    "content": section,
                    "source": doc_path.name,
                    "title": section.split("\n")[0].replace("#", "").strip(),
                }
            )
    _chunk_cache = chunks
    return chunks


def retrieve_policy_chunks(query: str, limit: int = 3, min_score: float = 0.1) -> list[dict]:
    """
    Búsqueda por palabras clave (fallback sin embeddings).
    Retorna fragmentos con fuente.
    """
    query_terms = {t.lower() for t in query.split() if len(t) > 3}
    if not query_terms:
        return []

    scored: list[tuple[float, dict]] = []
    for chunk in _load_chunks():
        text_lower = chunk["content"].lower()
        matches = sum(1 for term in query_terms if term in text_lower)
        if matches == 0:
            continue
        score = matches / len(query_terms)
        if score >= min_score:
            scored.append((score, {**chunk, "score": round(score, 2)}))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]
