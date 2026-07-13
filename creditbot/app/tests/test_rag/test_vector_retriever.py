"""Pruebas del retriever RAG vectorial."""
from app.rag.ingest import ingest_all
from app.rag.retriever import retrieve_policy_chunks


def test_vector_retrieval_after_ingest():
    count = ingest_all()
    assert count >= 3
    chunks = retrieve_policy_chunks("precalificación plazos máximos")
    assert len(chunks) > 0
    assert chunks[0]["source"]


def test_rag_no_evidence_short_query():
    chunks = retrieve_policy_chunks("xyz")
    assert chunks == []
