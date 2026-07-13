#!/usr/bin/env python3
"""Script de pruebas manuales v3 del simulador."""
import json
import sys

import httpx

BASE = "http://127.0.0.1:8000"
PHONE = "593555555101"
CEDULA_EXCELENTE = "1713175071"

FLOW = [
    "Hola",
    "1",
    "Sí acepto",
    CEDULA_EXCELENTE,
    "Gano 2000 al mes",
    "Trabajo dependiente en una empresa",
    "400",
    "24",
    "Educación de mis hijos",
    "1",
]


def main():
    print("=== CrediBot v3 — Prueba de flujo simulador ===\n")
    for step, message in enumerate(FLOW, 1):
        response = httpx.post(
            f"{BASE}/simulate/message",
            json={"phone": PHONE, "message": message},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        print(f"Paso {step}: {message}")
        print(f"  modo={data.get('agent_mode')} estado={data.get('state')}")
        print(f"  respuesta: {data['reply'][:200]}...\n")

    print("=== Pregunta RAG ===")
    rag_resp = httpx.post(
        f"{BASE}/simulate/message",
        json={"phone": PHONE, "message": "¿Cuál es el plazo máximo del crédito?"},
        timeout=30,
    )
    print(json.dumps(rag_resp.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except httpx.ConnectError:
        print("Error: levanta el servidor con uvicorn app.main:app --reload", file=sys.stderr)
        sys.exit(1)
