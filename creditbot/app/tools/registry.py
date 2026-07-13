"""Registro de tools disponibles para el agente."""
from typing import Any, Callable

from app.tools.base import TimedTool, ToolResponse
from app.tools.cedula_tools import consultar_perfil_crediticio, validar_cedula, verificar_identidad
from app.tools.credit_tools import calcular_monto_maximo, derivar_a_asesor, registrar_solicitud
from app.tools.policy_tools import obtener_politica_credito

ToolHandler = Callable[..., ToolResponse]

TOOL_REGISTRY: dict[str, ToolHandler] = {
    "validar_cedula": validar_cedula,
    "consultar_perfil_crediticio": consultar_perfil_crediticio,
    "verificar_identidad": verificar_identidad,
    "calcular_monto_maximo": calcular_monto_maximo,
    "registrar_solicitud": registrar_solicitud,
    "derivar_a_asesor": derivar_a_asesor,
    "obtener_politica_credito": obtener_politica_credito,
}

TOOLS_BY_STATE: dict[str, set[str]] = {
    "ASK_CEDULA": {"validar_cedula", "consultar_perfil_crediticio", "verificar_identidad"},
    "ASK_INCOME": {"calcular_monto_maximo"},
    "ASK_PURPOSE": {"calcular_monto_maximo", "registrar_solicitud"},
    "CONFIRM": {"registrar_solicitud", "derivar_a_asesor"},
    "MENU": {"obtener_politica_credito", "derivar_a_asesor"},
    "CONSENTIMIENTO": {"obtener_politica_credito"},
    "*": {"obtener_politica_credito", "derivar_a_asesor"},
}


def get_allowed_tools(state: str) -> set[str]:
    """Retorna tools permitidas para un estado."""
    allowed = set(TOOLS_BY_STATE.get("*", set()))
    allowed.update(TOOLS_BY_STATE.get(state, set()))
    return allowed


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    conversation_id: str | None = None,
    state: str | None = None,
) -> ToolResponse:
    """Ejecuta una tool con auditoría y validación de estado."""
    if state and tool_name not in get_allowed_tools(state):
        return ToolResponse(success=False, error_code="tool_not_allowed")

    handler = TOOL_REGISTRY.get(tool_name)
    if not handler:
        return ToolResponse(success=False, error_code="tool_not_found")

    return TimedTool.run(tool_name, handler, arguments, conversation_id)


def get_openai_tool_schemas() -> list[dict[str, Any]]:
    """Esquemas de function calling para OpenAI."""
    return [
        {
            "type": "function",
            "function": {
                "name": "validar_cedula",
                "description": "Valida cédula ecuatoriana de 10 dígitos",
                "parameters": {
                    "type": "object",
                    "properties": {"cedula": {"type": "string"}},
                    "required": ["cedula"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "consultar_perfil_crediticio",
                "description": "Consulta perfil crediticio ficticio por cédula",
                "parameters": {
                    "type": "object",
                    "properties": {"cedula": {"type": "string"}},
                    "required": ["cedula"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calcular_monto_maximo",
                "description": "Calcula precalificación con reglas deterministas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cedula": {"type": "string"},
                        "monthly_income": {"type": "number"},
                        "monthly_expenses": {"type": "number"},
                        "term_months": {"type": "integer"},
                    },
                    "required": ["cedula", "monthly_income", "monthly_expenses", "term_months"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "obtener_politica_credito",
                "description": "Busca políticas y FAQs de crédito",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "derivar_a_asesor",
                "description": "Deriva conversación a asesor humano",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "conversation_id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["user_id", "conversation_id", "reason"],
                },
            },
        },
    ]
