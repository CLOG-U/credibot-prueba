"""Prueba E2E del simulador v2."""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PHONE = "593888888001"
CEDULA = "1713175071"
PROFILE = {
    "cedula": CEDULA,
    "full_name": "María Fernanda Vega",
    "credit_score": 820,
    "score_category": "excelente",
    "monthly_debt_payment": 180.0,
    "has_delinquency": False,
    "delinquency_days": 0,
    "is_blacklisted": False,
    "no_credit_history": False,
}


def _post(message: str):
    return client.post("/simulate/message", json={"phone": PHONE, "message": message})


@patch("app.services.conversation_service.credit_profile_repository.get_profile_by_cedula")
@patch("app.services.conversation_service.user_repository.get_or_create_user")
@patch("app.services.conversation_service.conversation_repository.get_or_create_active_conversation")
@patch("app.services.conversation_service.message_repository.save_inbound_message")
@patch("app.services.conversation_service.message_repository.save_outbound_message")
@patch("app.services.conversation_service.conversation_repository.update_state")
@patch("app.services.conversation_service.conversation_repository.update_last_message")
@patch("app.services.conversation_service.conversation_repository.reset_validation_failures")
@patch("app.services.conversation_service.conversation_repository.increment_validation_failures")
def test_e2e_simulator_v2_flow(
    mock_inc,
    mock_reset,
    mock_last,
    mock_state,
    mock_out,
    mock_in,
    mock_conv,
    mock_user,
    mock_profile,
):
    from app.core.constants import (
        ASK_CEDULA,
        ASK_EMPLOYMENT,
        ASK_EXPENSES,
        ASK_INCOME,
        ASK_PURPOSE,
        ASK_TERM,
        CONFIRM,
        CONSENTIMIENTO,
        FINISHED,
        MENU,
        START,
    )

    states = [
        START,
        MENU,
        CONSENTIMIENTO,
        ASK_CEDULA,
        ASK_INCOME,
        ASK_EMPLOYMENT,
        ASK_EXPENSES,
        ASK_TERM,
        ASK_PURPOSE,
        CONFIRM,
        FINISHED,
    ]
    idx = {"i": 0}
    mock_user.return_value = {"id": "u1", "phone": PHONE}
    mock_profile.return_value = PROFILE
    mock_inc.return_value = 1
    mock_reset.return_value = None

    def conv(_uid):
        return {"id": "c1", "user_id": "u1", "current_state": states[idx["i"]], "validation_failures": 0}

    def upd(_cid, ns):
        idx["i"] = states.index(ns)

    mock_conv.side_effect = conv
    mock_state.side_effect = upd

    draft = {"id": "r1", "user_id": "u1", "conversation_id": "c1", "status": "draft", "cedula": CEDULA}

    with patch(
        "app.services.conversation_service.credit_repository.create_draft_request",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.get_draft_request",
        return_value={
            **draft,
            "monthly_income": 2000.0,
            "employment_type": "dependiente",
            "monthly_expenses": 300.0,
            "term_months": 24,
            "loan_purpose": "educacion",
        },
    ), patch(
        "app.services.conversation_service.credit_repository.update_profile_data",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.user_repository.update_user_consent",
        return_value={"id": "u1"},
    ), patch(
        "app.services.conversation_service.credit_repository.update_income",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.update_employment",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.update_expenses",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.update_term",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.update_purpose",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.save_result",
        return_value={**draft, "status": "completed"},
    ), patch(
        "app.services.conversation_service.conversation_repository.finish_conversation",
        return_value=conv("u1"),
    ):
        assert _post("Hola").status_code == 200
        assert _post("1").status_code == 200
        assert _post("1").status_code == 200
        assert _post(CEDULA).status_code == 200
        assert _post("2000").status_code == 200
        assert _post("dependiente").status_code == 200
        assert _post("300").status_code == 200
        assert _post("24").status_code == 200
        final = _post("educacion")
        assert final.status_code == 200
        assert "Resultado" in final.json()["reply"]
        done = _post("1")
        assert done.status_code == 200
        assert "registrada" in done.json()["reply"].lower()
