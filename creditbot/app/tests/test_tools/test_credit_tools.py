"""Pruebas de tools crediticias."""
from unittest.mock import patch

from app.tools.cedula_tools import consultar_perfil_crediticio, validar_cedula
from app.tools.credit_tools import calcular_monto_maximo
from app.tools.policy_tools import obtener_politica_credito


def test_validar_cedula_ok():
    result = validar_cedula("1713175071")
    assert result.success is True
    assert result.data["cedula"] == "1713175071"


def test_validar_cedula_invalid():
    result = validar_cedula("123")
    assert result.success is False


@patch("app.tools.cedula_tools.credit_profile_repository.get_profile_by_cedula")
def test_consultar_perfil(mock_get):
    mock_get.return_value = {
        "full_name": "Test User",
        "credit_score": 820,
        "score_category": "excelente",
        "monthly_debt_payment": 100,
        "has_delinquency": False,
        "delinquency_days": 0,
        "is_blacklisted": False,
        "no_credit_history": False,
    }
    result = consultar_perfil_crediticio("1713175071")
    assert result.success is True
    assert result.data["credit_score"] == 820


@patch("app.tools.credit_tools.consultar_perfil_crediticio")
def test_calcular_monto_maximo(mock_profile):
    from app.tools.base import ToolResponse

    mock_profile.return_value = ToolResponse(
        success=True,
        data={
            "credit_score": 820,
            "score_category": "excelente",
            "monthly_debt_payment": 100,
            "has_delinquency": False,
            "delinquency_days": 0,
            "is_blacklisted": False,
            "no_credit_history": False,
        },
    )
    result = calcular_monto_maximo(
        cedula="1713175071",
        monthly_income=2000,
        monthly_expenses=300,
        term_months=24,
    )
    assert result.success is True
    assert result.data["result"] == "preaprobado"


def test_obtener_politica_credito():
    result = obtener_politica_credito("precalificación aprobación")
    assert result.success is True
    assert len(result.data["chunks"]) > 0
    assert result.data["sources"]
