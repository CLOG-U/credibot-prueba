"""Tools de cédula e identidad."""
from app.domain.cedula_validator import mask_cedula, normalize_cedula, validate_cedula
from app.domain.credit_rules import evaluate_eligibility, CreditProfileInput
from app.repositories import credit_profile_repository
from app.tools.base import ToolResponse


def validar_cedula(cedula: str, **_) -> ToolResponse:
    """Valida formato y dígito verificador de cédula."""
    is_valid, error_code = validate_cedula(cedula)
    if not is_valid:
        return ToolResponse(success=False, error_code=error_code)
    return ToolResponse(
        success=True,
        data={"cedula": normalize_cedula(cedula), "cedula_masked": mask_cedula(cedula)},
    )


def consultar_perfil_crediticio(cedula: str, **_) -> ToolResponse:
    """Consulta perfil ficticio por cédula."""
    normalized = normalize_cedula(cedula)
    is_valid, error_code = validate_cedula(normalized)
    if not is_valid:
        return ToolResponse(success=False, error_code=error_code)

    profile = credit_profile_repository.get_profile_by_cedula(normalized)
    if not profile:
        return ToolResponse(success=False, error_code="profile_not_found")

    return ToolResponse(
        success=True,
        data={
            "cedula_masked": mask_cedula(normalized),
            "full_name": profile["full_name"],
            "credit_score": profile["credit_score"],
            "score_category": profile["score_category"],
            "has_delinquency": profile.get("has_delinquency", False),
            "delinquency_days": profile.get("delinquency_days", 0),
            "is_blacklisted": profile.get("is_blacklisted", False),
            "no_credit_history": profile.get("no_credit_history", False),
            "monthly_debt_payment": float(profile.get("monthly_debt_payment") or 0),
        },
    )


def verificar_identidad(cedula: str, **_) -> ToolResponse:
    """Valida cédula y evalúa elegibilidad del perfil."""
    profile_response = consultar_perfil_crediticio(cedula)
    if not profile_response.success:
        return profile_response

    data = profile_response.data
    eligibility = evaluate_eligibility(
        CreditProfileInput(
            credit_score=int(data["credit_score"]),
            score_category=str(data["score_category"]),
            monthly_debt_payment=float(data["monthly_debt_payment"]),
            has_delinquency=bool(data["has_delinquency"]),
            delinquency_days=int(data["delinquency_days"]),
            is_blacklisted=bool(data["is_blacklisted"]),
            no_credit_history=bool(data["no_credit_history"]),
        )
    )
    return ToolResponse(
        success=True,
        data={
            **data,
            "eligibility_status": eligibility.status,
            "eligibility_reasons": eligibility.reasons,
            "effective_category": eligibility.effective_category,
        },
    )
