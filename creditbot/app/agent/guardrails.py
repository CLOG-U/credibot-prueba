"""Guardrails de salida del agente GPT."""
import re
from typing import Any

INJECTION_PATTERNS = [
    r"ignora\s+las\s+instrucciones",
    r"system\s+prompt",
    r"act[uú]a\s+como\s+administrador",
    r"clave\s+de\s+supabase",
    r"api\s*key",
    r"cambia\s+mi\s+resultado",
    r"apru[eé]bame",
]

FORBIDDEN_OUTPUT = [
    r"score\s*(?:de\s*|es\s*)?\d{2,3}",
    r"score.*?\d{2,3}",
    r"\$\s*\d+[\d,.]*",
    r"\bpreaprobado\b",
    r"\bobservado\b",
    r"\bno_cumple\b",
    r"\baprobado\s+definitiv",
    r"\b\d{10}\b",
]


def detect_prompt_injection(user_message: str) -> bool:
    """Detecta intentos básicos de prompt injection."""
    lowered = user_message.lower()
    return any(re.search(p, lowered) for p in INJECTION_PATTERNS)


def validate_agent_output(
    content: str,
    tool_results: list[dict[str, Any]],
    canonical_response: str,
) -> str | None:
    """
    Valida salida GPT. Retorna código de error o None si es válida.
    Si hay tool_results con datos crediticios, permite cifras alineadas.
    """
    if not content.strip():
        return "empty_response"

    lowered = content.lower()
    has_credit_tools = any(
        r.get("tool") in {"calcular_monto_maximo", "consultar_perfil_crediticio", "verificar_identidad"}
        for r in tool_results
    )

    if not has_credit_tools:
        for pattern in FORBIDDEN_OUTPUT:
            if re.search(pattern, lowered):
                return "invented_credit_data"

    if "preaprobado" in canonical_response.lower() or "observado" in canonical_response.lower():
        if re.search(r"\bno\s+cumple\b", lowered) and "no cumple" not in canonical_response.lower():
            return "contradicts_canonical"

    return None
