"""Constructor de contexto seguro para el agente GPT."""
from typing import Any

from app.domain.cedula_validator import mask_cedula
from app.repositories import credit_repository, message_repository


class ConversationContextBuilder:
    """Arma contexto mínimo por estado sin exponer datos sensibles."""

    MAX_HISTORY = 8

    def build(
        self,
        conversation_id: str,
        state: str,
        user_id: str,
        draft_request: dict[str, Any] | None = None,
        canonical_response: str = "",
        tool_results: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        try:
            history = message_repository.get_messages_by_conversation(conversation_id)
        except Exception:
            history = []
        recent = history[-self.MAX_HISTORY :] if history else []

        context: dict[str, Any] = {
            "state": state,
            "expected_input": self._expected_input(state),
            "recent_messages": [
                {"role": m["direction"], "content": m["content"][:500]}
                for m in recent
            ],
            "canonical_response": canonical_response[:1500],
            "tool_results": tool_results or [],
        }

        if draft_request:
            context["validated_data"] = {
                "cedula_masked": mask_cedula(str(draft_request.get("cedula", "")))
                if draft_request.get("cedula")
                else None,
                "score_category": draft_request.get("score_category"),
                "monthly_income": draft_request.get("monthly_income"),
                "monthly_expenses": draft_request.get("monthly_expenses"),
                "term_months": draft_request.get("term_months"),
                "employment_type": draft_request.get("employment_type"),
                "loan_purpose": draft_request.get("loan_purpose"),
            }

        return context

    @staticmethod
    def _expected_input(state: str) -> str:
        mapping = {
            "MENU": "opción 1, 2 o 3",
            "CONSENTIMIENTO": "aceptación del aviso de privacidad",
            "ASK_CEDULA": "cédula ecuatoriana de 10 dígitos",
            "ASK_INCOME": "ingreso mensual",
            "ASK_EMPLOYMENT": "tipo de empleo",
            "ASK_EXPENSES": "gastos mensuales",
            "ASK_TERM": "plazo en meses (3-36)",
            "ASK_PURPOSE": "destino del crédito",
            "CONFIRM": "confirmación 1=Sí, 2=asesor",
        }
        return mapping.get(state, "dato del flujo")


def get_draft_for_conversation(conversation_id: str) -> dict[str, Any] | None:
    """Recupera solicitud draft activa."""
    return credit_repository.get_draft_request(conversation_id)
