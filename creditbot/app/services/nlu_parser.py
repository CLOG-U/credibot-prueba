"""Normalización de lenguaje natural para el flujo determinista."""
import re

from app.services import validation_service

TERM_WORDS = {
    "un año": 12,
    "una año": 12,
    "doce meses": 12,
    "12 meses": 12,
    "dieciocho meses": 18,
    "18 meses": 18,
    "dos años": 24,
    "24 meses": 24,
    "treinta y seis": 36,
    "36 meses": 36,
}

CONSENT_YES = {"si", "sí", "acepto", "aceptar", "de acuerdo", "continuemos", "ok", "vale", "1"}
CONSENT_NO = {"no", "rechazo", "rechazar", "2"}
CONFIRM_YES = {"si", "sí", "confirmo", "correcto", "está bien", "esta bien", "están bien", "estan bien", "de acuerdo", "1"}
CONFIRM_NO = {"no", "corregir", "2"}


def _extract_first_number(text: str) -> str | None:
    """Extrae el primer número de un texto."""
    cleaned = text.replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if match:
        return match.group(1)
    return None


def preprocess(state: str, text: str) -> str:
    """Normaliza entrada natural según el estado actual."""
    stripped = text.strip()
    lowered = stripped.lower()

    if state == "MENU":
        if any(w in lowered for w in ("precalif", "crédito", "credito", "solicitar")):
            return "1"
        if any(w in lowered for w in ("información", "informacion", "info")):
            return "2"
        if any(w in lowered for w in ("asesor", "humano", "persona")):
            return "3"

    if state == "CONSENTIMIENTO":
        if any(word in lowered for word in CONSENT_YES):
            return "1"
        if any(word in lowered for word in CONSENT_NO):
            return "2"

    if state == "ASK_INCOME":
        number = _extract_first_number(stripped)
        if number:
            return number

    if state == "ASK_EXPENSES":
        number = _extract_first_number(stripped)
        if number:
            return number

    if state == "ASK_TERM":
        for phrase, months in TERM_WORDS.items():
            if phrase in lowered:
                return str(months)
        number = _extract_first_number(stripped)
        if number:
            try:
                term = int(float(number))
                if 3 <= term <= 36:
                    return str(term)
            except ValueError:
                pass

    if state == "CONFIRM":
        if any(word in lowered for word in CONFIRM_YES):
            return "1"
        if any(word in lowered for word in CONFIRM_NO):
            return "2"

    if state == "ASK_CEDULA":
        digits = "".join(ch for ch in stripped if ch.isdigit())
        if len(digits) == 10:
            return digits

    return stripped


def parse_employment_type(text: str) -> str:
    """Clasifica tipo de empleo desde texto libre."""
    lowered = text.lower()
    if any(w in lowered for w in ("independ", "freelance", "propio")):
        return "independiente"
    if any(w in lowered for w in ("jubil", "pension")):
        return "jubilado"
    if any(w in lowered for w in ("depend", "empresa", "nomina", "nómina", "empleo")):
        return "dependiente"
    return text.strip()
