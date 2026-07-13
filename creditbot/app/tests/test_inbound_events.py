"""Pruebas de idempotencia de eventos entrantes."""
from unittest.mock import patch

from app.repositories import inbound_events_repository


@patch("app.repositories.inbound_events_repository.is_duplicate_event", return_value=True)
def test_try_claim_event_returns_false_when_duplicate(_mock_dup):
    assert inbound_events_repository.try_claim_event("twilio", "msg-1") is False


@patch("app.repositories.inbound_events_repository.get_supabase_client")
@patch("app.repositories.inbound_events_repository.is_duplicate_event", return_value=False)
def test_try_claim_event_inserts_before_processing(_mock_dup, mock_client):
    mock_client.return_value.table.return_value.insert.return_value.execute.return_value = None
    assert inbound_events_repository.try_claim_event("twilio", "msg-2", phone="5931") is True


@patch("app.repositories.inbound_events_repository.is_duplicate_event", return_value=False)
@patch("app.repositories.inbound_events_repository.get_supabase_client")
def test_try_claim_event_handles_race_on_insert(mock_client, _mock_dup):
    mock_client.return_value.table.return_value.insert.return_value.execute.side_effect = Exception(
        "duplicate"
    )
    assert inbound_events_repository.try_claim_event("twilio", "msg-3") is False
