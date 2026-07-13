"""Tool RAG de políticas crediticias."""
from app.rag.retriever import retrieve_policy_chunks
from app.tools.base import ToolResponse


def obtener_politica_credito(query: str, **_) -> ToolResponse:
    """Recupera fragmentos de políticas con fuentes."""
    chunks = retrieve_policy_chunks(query, limit=3)
    if not chunks:
        return ToolResponse(success=False, error_code="no_evidence")

    return ToolResponse(
        success=True,
        data={
            "query": query,
            "chunks": chunks,
            "sources": [c["source"] for c in chunks],
        },
    )
