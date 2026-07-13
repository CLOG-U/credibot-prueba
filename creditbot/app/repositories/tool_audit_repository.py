"""Registro de ejecución de tools."""
from typing import Any

from app.repositories.supabase_client import get_supabase_client


def log_tool_execution(
    tool_name: str,
    input_payload: dict[str, Any] | None,
    output_payload: dict[str, Any] | None,
    conversation_id: str | None = None,
    trace_id: str | None = None,
    success: bool = True,
    error_code: str | None = None,
    latency_ms: int = 0,
) -> dict[str, Any] | None:
    """Guarda auditoría de una tool invocada."""
    payload = {
        "tool_name": tool_name,
        "input_payload": input_payload,
        "output_payload": output_payload,
        "conversation_id": conversation_id,
        "trace_id": trace_id,
        "success": success,
        "error_code": error_code,
        "latency_ms": latency_ms,
    }
    response = get_supabase_client().table("tool_audit_logs").insert(payload).execute()
    if response.data:
        return response.data[0]
    return None
