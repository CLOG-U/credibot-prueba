"""Pruebas de memoria y aislamiento de sesión."""
from unittest.mock import patch

from app.session.session_store import InMemorySessionStore, sync_session_from_conversation


def test_sync_session_from_conversation_isolated_per_user():
    store = InMemorySessionStore()
    conv_a = {"id": "c-a", "current_state": "ASK_INCOME", "validation_failures": 0, "user_id": "u-a"}
    conv_b = {"id": "c-b", "current_state": "ASK_CEDULA", "validation_failures": 1, "user_id": "u-b"}

    with patch("app.session.session_store.get_session_store", return_value=store):
        sync_session_from_conversation(conv_a)
        sync_session_from_conversation(conv_b)

    assert store.get("c-a")["state"] == "ASK_INCOME"
    assert store.get("c-b")["state"] == "ASK_CEDULA"
    assert store.get("c-a")["user_id"] != store.get("c-b")["user_id"]


@patch("app.session.session_store.get_session_store")
@patch("app.session.session_store.load_session_from_supabase")
def test_get_or_recover_session_falls_back_to_supabase(mock_load, mock_store_fn):
    from app.session.session_store import get_or_recover_session

    store = InMemorySessionStore()
    mock_store_fn.return_value = store
    mock_load.return_value = {"state": "MENU", "validation_failures": 0, "user_id": "u1"}

    data = get_or_recover_session("conv-recover")

    assert data is not None
    assert data["state"] == "MENU"
