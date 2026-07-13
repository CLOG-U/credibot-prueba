"""Prueba de aislamiento entre dos usuarios concurrentes (mock)."""
from unittest.mock import patch

from app.services.conversation_service import process_message

USER_A = {"id": "ua", "phone": "593111111001"}
USER_B = {"id": "ub", "phone": "593222222002"}


def _conv(cid, uid, state):
    return {"id": cid, "user_id": uid, "current_state": state, "validation_failures": 0}


@patch("app.services.conversation_service.message_repository.save_outbound_message")
@patch("app.services.conversation_service.message_repository.save_inbound_message")
@patch("app.services.conversation_service.conversation_repository.update_last_message")
@patch("app.services.conversation_service.conversation_repository.update_state")
@patch("app.services.conversation_service.conversation_repository.reset_validation_failures")
@patch("app.services.conversation_service.sync_session_from_conversation")
@patch("app.services.conversation_service.get_or_recover_session")
@patch("app.services.conversation_service.conversation_repository.get_or_create_active_conversation")
@patch("app.services.conversation_service.user_repository.get_or_create_user")
def test_two_users_isolated_states(
    mock_user,
    mock_conv,
    mock_recover,
    mock_sync,
    mock_reset,
    mock_state,
    mock_last,
    mock_in,
    mock_out,
):
    calls = {"a": 0, "b": 0}

    def user_side(phone):
        return USER_A if phone.endswith("1001") else USER_B

    def conv_side(uid):
        if uid == "ua":
            calls["a"] += 1
            return _conv("ca", "ua", "START" if calls["a"] == 1 else "MENU")
        calls["b"] += 1
        return _conv("cb", "ub", "START" if calls["b"] == 1 else "MENU")

    mock_user.side_effect = user_side
    mock_conv.side_effect = conv_side
    mock_reset.return_value = None

    with patch("app.core.config.settings.enable_gpt_agent", False):
        reply_a = process_message("593111111001", "Hola")
        reply_b = process_message("593222222002", "Hola")

    assert "CrediBot" in reply_a
    assert "CrediBot" in reply_b
    assert mock_conv.call_count == 2
