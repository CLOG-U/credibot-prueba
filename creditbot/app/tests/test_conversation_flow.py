"""Pruebas del flujo conversacional v2."""
from unittest.mock import patch

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
from app.services.conversation_service import _contains_handoff_keyword, process_message

USER_ID = "user-1"
CONVERSATION_ID = "conv-1"
REQUEST_ID = "req-1"
CEDULA = "1713175071"

PROFILE = {
    "id": "profile-1",
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


def _base_user():
    return {"id": USER_ID, "phone": "593999999999", "full_name": None}


def _base_conversation(state: str = START):
    return {
        "id": CONVERSATION_ID,
        "user_id": USER_ID,
        "current_state": state,
        "is_active": True,
        "validation_failures": 0,
    }


def _draft_request(**overrides):
    data = {
        "id": REQUEST_ID,
        "user_id": USER_ID,
        "conversation_id": CONVERSATION_ID,
        "cedula": CEDULA,
        "credit_score": 820,
        "score_category": "excelente",
        "monthly_income": None,
        "monthly_expenses": None,
        "term_months": None,
        "employment_type": None,
        "loan_purpose": None,
        "status": "draft",
    }
    data.update(overrides)
    return data


V2_STATES = [
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


@patch("app.services.conversation_service.message_repository.save_outbound_message")
@patch("app.services.conversation_service.message_repository.save_inbound_message")
@patch("app.services.conversation_service.conversation_repository.update_last_message")
@patch("app.services.conversation_service.conversation_repository.update_state")
@patch("app.services.conversation_service.conversation_repository.reset_validation_failures")
@patch("app.services.conversation_service.conversation_repository.increment_validation_failures")
@patch("app.services.conversation_service.credit_profile_repository.get_profile_by_cedula")
@patch("app.services.conversation_service.credit_repository.get_draft_request")
@patch("app.services.conversation_service.credit_repository.create_draft_request")
@patch("app.services.conversation_service.conversation_repository.get_or_create_active_conversation")
@patch("app.services.conversation_service.user_repository.get_or_create_user")
def test_conversation_flow_v2_excellent(
    mock_get_user,
    mock_get_conversation,
    mock_create_draft,
    mock_get_draft,
    mock_get_profile,
    mock_increment_failures,
    mock_reset_failures,
    mock_update_state,
    mock_update_last_message,
    mock_save_inbound,
    mock_save_outbound,
):
    """Flujo v2 completo con perfil excelente."""
    user = _base_user()
    mock_get_user.return_value = user
    mock_get_profile.return_value = PROFILE
    mock_increment_failures.return_value = 1
    mock_reset_failures.return_value = None

    state_index = {"value": 0}

    def conversation_side_effect(_user_id):
        return _base_conversation(V2_STATES[state_index["value"]])

    def update_state_side_effect(_conversation_id, new_state):
        state_index["value"] = V2_STATES.index(new_state)

    mock_get_conversation.side_effect = conversation_side_effect
    mock_update_state.side_effect = update_state_side_effect

    draft = _draft_request()
    mock_get_draft.side_effect = [
        draft,
        _draft_request(monthly_income=2000),
        _draft_request(monthly_income=2000, employment_type="dependiente"),
        _draft_request(monthly_income=2000, employment_type="dependiente", monthly_expenses=300),
        _draft_request(
            monthly_income=2000,
            employment_type="dependiente",
            monthly_expenses=300,
            term_months=24,
        ),
        _draft_request(
            monthly_income=2000,
            employment_type="dependiente",
            monthly_expenses=300,
            term_months=24,
            loan_purpose="educación",
            cedula=CEDULA,
        ),
        _draft_request(
            monthly_income=2000,
            employment_type="dependiente",
            monthly_expenses=300,
            term_months=24,
            loan_purpose="educación",
            cedula=CEDULA,
        ),
    ]

    with patch(
        "app.services.conversation_service.user_repository.update_user_consent",
        return_value=user,
    ), patch(
        "app.services.conversation_service.credit_repository.update_profile_data",
        return_value=draft,
    ), patch(
        "app.services.conversation_service.credit_repository.update_income",
        return_value=_draft_request(monthly_income=2000),
    ), patch(
        "app.services.conversation_service.credit_repository.update_employment",
        return_value=_draft_request(monthly_income=2000, employment_type="dependiente"),
    ), patch(
        "app.services.conversation_service.credit_repository.update_expenses",
        return_value=_draft_request(
            monthly_income=2000, employment_type="dependiente", monthly_expenses=300
        ),
    ), patch(
        "app.services.conversation_service.credit_repository.update_term",
        return_value=_draft_request(
            monthly_income=2000,
            employment_type="dependiente",
            monthly_expenses=300,
            term_months=24,
        ),
    ), patch(
        "app.services.conversation_service.credit_repository.update_purpose",
        return_value=_draft_request(
            monthly_income=2000,
            employment_type="dependiente",
            monthly_expenses=300,
            term_months=24,
            loan_purpose="educación",
            cedula=CEDULA,
        ),
    ), patch(
        "app.services.conversation_service.credit_repository.save_result",
        return_value=_draft_request(status="completed"),
    ), patch(
        "app.services.conversation_service.conversation_repository.finish_conversation",
        return_value=_base_conversation(FINISHED),
    ), patch("app.core.config.settings.enable_gpt_agent", False):
        assert "precalificación" in process_message("593999999999", "Hola").lower()
        assert "aceptas" in process_message("593999999999", "1").lower()
        mock_create_draft.assert_called_once()
        assert "cédula" in process_message("593999999999", "1").lower()
        assert "Identidad verificada" in process_message("593999999999", CEDULA)
        assert "laboral" in process_message("593999999999", "2000").lower()
        assert "gastos" in process_message("593999999999", "dependiente").lower()
        assert "meses" in process_message("593999999999", "300").lower()
        assert "destinarías" in process_message("593999999999", "24").lower()
        assert "registrar" in process_message("593999999999", "educacion").lower()
        result_reply = process_message("593999999999", "1")
        assert "registrada" in result_reply.lower()


def test_contains_handoff_keyword():
    """Verifica palabras clave de derivación."""
    assert _contains_handoff_keyword("quiero hablar con un asesor") is True
    assert _contains_handoff_keyword("impersonal") is False
    assert _contains_handoff_keyword("necesito un agente") is True
