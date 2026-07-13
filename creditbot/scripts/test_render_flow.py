#!/usr/bin/env python3
"""Smoke test del flujo en Render."""
import httpx

BASE = "https://credibot-prueba.onrender.com/simulate/message"
PHONE = "593555555505"
FLOW = ["Hola", "1", "1", "1713175071", "2000", "dependiente", "300", "24", "educacion", "1"]


def main() -> None:
    last = {}
    for step, message in enumerate(FLOW, 1):
        response = httpx.post(BASE, json={"phone": PHONE, "message": message}, timeout=120)
        response.raise_for_status()
        last = response.json()
        print(
            f"Paso {step}: {message!r} -> "
            f"state={last.get('state')} mode={last.get('agent_mode')} tokens={last.get('tokens')}"
        )
    print("Respuesta final:", last.get("reply", "")[:200])


if __name__ == "__main__":
    main()
