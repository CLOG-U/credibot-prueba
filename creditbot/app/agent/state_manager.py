"""Constantes y utilidades del flujo conversacional v2."""

from app.core.constants import (
    ASK_CEDULA,
    ASK_EMPLOYMENT,
    ASK_EXPENSES,
    ASK_INCOME,
    ASK_PURPOSE,
    ASK_TERM,
    CONSENTIMIENTO,
    CONFIRM,
    FINISHED,
    HANDOFF_REQUESTED,
    SHOW_RESULT,
)

TERMINAL_STATES = {HANDOFF_REQUESTED, FINISHED}

FLOW_AFTER_CONSENT = [
    CONSENTIMIENTO,
    ASK_CEDULA,
    ASK_INCOME,
    ASK_EMPLOYMENT,
    ASK_EXPENSES,
    ASK_TERM,
    ASK_PURPOSE,
    SHOW_RESULT,
    CONFIRM,
    FINISHED,
]


def is_terminal_state(state: str) -> bool:
    """Indica si el estado cierra o deriva la conversación."""
    return state in TERMINAL_STATES
