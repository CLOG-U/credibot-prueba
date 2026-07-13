"""Contratos comunes para tools auditables."""
import copy
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.domain.cedula_validator import mask_cedula
from app.repositories import tool_audit_repository


def _mask_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Enmascara cédulas en payloads de auditoría."""
    masked = copy.deepcopy(payload)
    if "cedula" in masked and masked["cedula"]:
        masked["cedula"] = mask_cedula(str(masked["cedula"]))
    return masked


@dataclass
class ToolResponse:
    """Respuesta estándar de una tool."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error_code": self.error_code,
            "trace_id": self.trace_id,
            "latency_ms": self.latency_ms,
        }


def audit_tool_call(
    tool_name: str,
    input_payload: dict[str, Any],
    response: ToolResponse,
    conversation_id: str | None = None,
    latency_ms: int = 0,
) -> None:
    """Registra ejecución de tool en auditoría."""
    try:
        tool_audit_repository.log_tool_execution(
            tool_name=tool_name,
            input_payload=_mask_payload(input_payload),
            output_payload=response.to_dict(),
            conversation_id=conversation_id,
            trace_id=response.trace_id,
            success=response.success,
            error_code=response.error_code,
            latency_ms=latency_ms,
        )
    except Exception:
        pass


class TimedTool:
    """Envoltorio para medir latencia de tools."""

    @staticmethod
    def run(
        tool_name: str,
        handler,
        input_payload: dict[str, Any],
        conversation_id: str | None = None,
    ) -> ToolResponse:
        start = time.perf_counter()
        response = handler(**input_payload)
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.latency_ms = latency_ms
        audit_tool_call(tool_name, input_payload, response, conversation_id, latency_ms)
        return response
