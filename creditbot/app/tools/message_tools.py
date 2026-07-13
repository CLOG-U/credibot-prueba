"""Tool para registrar mensajes."""
from typing import Any

from app.repositories import message_repository
from app.tools.base import ToolResponse


def registrar_mensaje(
    conversation_id: str,
    user_id: str,
    direction: str,
    content: str,
    **_,
) -> ToolResponse:
    """Registra un mensaje en la conversación."""
    if direction not in {"inbound", "outbound"}:
        return ToolResponse(success=False, error_code="invalid_direction")

    try:
        if direction == "inbound":
            saved = message_repository.save_inbound_message(conversation_id, user_id, content)
        else:
            saved = message_repository.save_outbound_message(conversation_id, user_id, content)
        return ToolResponse(success=True, data={"message_id": saved["id"], "direction": direction})
    except Exception:
        return ToolResponse(success=False, error_code="save_failed")
