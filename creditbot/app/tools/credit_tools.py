"""Tools de cálculo y solicitud crediticia."""
from app.domain.credit_rules import CreditProfileInput, evaluate_precalification
from app.repositories import credit_repository, handoff_repository
from app.tools.base import ToolResponse
from app.tools.cedula_tools import consultar_perfil_crediticio


def calcular_monto_maximo(
    cedula: str,
    monthly_income: float,
    monthly_expenses: float,
    term_months: int,
    **_,
) -> ToolResponse:
    """Calcula precalificación determinista."""
    profile_response = consultar_perfil_crediticio(cedula)
    if not profile_response.success:
        return profile_response

    profile_data = profile_response.data
    profile_input = CreditProfileInput(
        credit_score=int(profile_data["credit_score"]),
        score_category=str(profile_data["score_category"]),
        monthly_debt_payment=float(profile_data["monthly_debt_payment"]),
        has_delinquency=bool(profile_data["has_delinquency"]),
        delinquency_days=int(profile_data["delinquency_days"]),
        is_blacklisted=bool(profile_data["is_blacklisted"]),
        no_credit_history=bool(profile_data["no_credit_history"]),
    )
    result = evaluate_precalification(
        profile=profile_input,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        term_months=term_months,
    )
    return ToolResponse(
        success=True,
        data={
            "result": result.result,
            "max_amount": result.max_amount,
            "suggested_amount": result.suggested_amount,
            "annual_rate": result.annual_rate,
            "monthly_payment": result.monthly_payment,
            "payment_capacity": result.payment_capacity,
            "category": result.category,
            "reasons": result.reasons,
            "rules_version": result.rules_version,
        },
    )


def registrar_solicitud(
    request_id: str,
    monthly_payment: float,
    payment_capacity: float,
    result: str,
    **extra_fields,
) -> ToolResponse:
    """Registra resultado de solicitud."""
    existing = credit_repository.get_request_by_id(request_id)
    if existing and existing.get("status") == "completed":
        return ToolResponse(
            success=True,
            data={"request_id": existing["id"], "status": existing["status"], "idempotent": True},
        )
    try:
        saved = credit_repository.save_result(
            request_id,
            monthly_payment,
            payment_capacity,
            result,
            **extra_fields,
        )
        return ToolResponse(success=True, data={"request_id": saved["id"], "status": saved["status"]})
    except Exception:
        return ToolResponse(success=False, error_code="save_failed")


def derivar_a_asesor(
    user_id: str,
    conversation_id: str,
    reason: str,
    credit_request_id: str | None = None,
    **_,
) -> ToolResponse:
    """Crea caso de derivación a asesor."""
    pending = handoff_repository.get_pending_case_for_conversation(conversation_id)
    if pending:
        return ToolResponse(
            success=True,
            data={"handoff_id": pending["id"], "status": pending["status"], "idempotent": True},
        )
    try:
        case = handoff_repository.create_handoff_case(
            user_id=user_id,
            conversation_id=conversation_id,
            reason=reason,
            credit_request_id=credit_request_id,
        )
        return ToolResponse(success=True, data={"handoff_id": case["id"], "status": case["status"]})
    except Exception:
        return ToolResponse(success=False, error_code="handoff_failed")
