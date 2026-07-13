#!/usr/bin/env python3
"""Evalúa hit rate del RAG con el dataset de docs/rag/evaluacion.md."""
import re
from pathlib import Path

from app.rag.retriever import retrieve_policy_chunks

QUESTIONS = [
    ("¿Qué es una precalificación?", ["precalif", "estim"]),
    ("¿Es una aprobación final?", ["no", "estim"]),
    ("¿Cuál es el plazo máximo?", ["36", "mes"]),
    ("¿Puedo hablar con un asesor?", ["asesor", "sí", "si"]),
    ("¿Usan datos reales?", ["fictic", "acad", "no"]),
    ("¿Qué categorías de score existen?", ["excelente", "aceptable", "regular"]),
    ("¿Qué TEA tiene categoría excelente?", ["14", "14.5"]),
    ("¿Se pide consentimiento?", ["consent", "sí", "si", "acept"]),
    ("¿Qué documentos necesito después?", ["cédula", "cedula", "rol"]),
    ("¿Pueden desembolsar dinero?", ["no", "precalif"]),
]


def _has_evidence(chunks: list[dict], keywords: list[str]) -> bool:
    if not chunks:
        return False
    text = " ".join(c["content"].lower() for c in chunks)
    return any(k in text for k in keywords)


def main() -> None:
    hits = 0
    for question, keywords in QUESTIONS:
        chunks = retrieve_policy_chunks(question)
        ok = _has_evidence(chunks, keywords)
        hits += int(ok)
        status = "OK" if ok else "MISS"
        sources = ", ".join(c.get("source", "") for c in chunks[:2])
        print(f"[{status}] {question} -> {sources or 'sin evidencia'}")

    total = len(QUESTIONS)
    rate = round((hits / total) * 100, 1) if total else 0
    print(f"\nHit rate: {hits}/{total} ({rate}%)")


if __name__ == "__main__":
    main()
