"""Pruebas del retriever RAG."""
from app.rag.retriever import retrieve_policy_chunks


def test_retrieve_policy_chunks():
    chunks = retrieve_policy_chunks("precalificación plazos")
    assert len(chunks) > 0
    assert "source" in chunks[0]
    assert chunks[0]["score"] > 0


def test_retrieve_no_evidence():
    chunks = retrieve_policy_chunks("xyz")
    assert chunks == []
