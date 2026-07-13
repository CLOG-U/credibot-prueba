"""Pruebas de integración GPT en conversation_service."""
from unittest.mock import patch

from app.core.constants import START
from app.services.conversation_service import get_last_agent_metadata, process_message

USER = {"id": "u-gpt", "phone": "593666666001"}


def _conv(state):
    return {"id": "c-gpt", "user_id": "u-gpt", "current_state": state, "validation_failures": 0}


@patch("app.services.conversation_service.conversation_repository.reset_validation_failures")
@patch("app.services.conversation_service.message_repository.save_outbound_message")
@patch("app.services.conversation_service.message_repository.save_inbound_message")
@patch("app.services.conversation_service.conversation_repository.update_last_message")
@patch("app.services.conversation_service.conversation_repository.update_state")
@patch("app.services.conversation_service.get_or_recover_session")
@patch("app.services.conversation_service.sync_session_from_conversation")
@patch("app.services.conversation_service.conversation_repository.get_or_create_active_conversation")
@patch("app.services.conversation_service.user_repository.get_or_create_user")
def test_agent_disabled_returns_deterministic_mode(
    mock_user,
    mock_conv,
    mock_sync,
    mock_recover,
    mock_state,
    mock_last,
    mock_in,
    mock_out,
    mock_reset,
):
    mock_user.return_value = USER
    mock_conv.return_value = _conv(START)
    mock_reset.return_value = None

    with patch("app.core.config.settings.enable_gpt_agent", False):
        process_message("593666666001", "Hola")

    meta = get_last_agent_metadata("c-gpt")
    assert meta.get("mode") == "deterministic"
