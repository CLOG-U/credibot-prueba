"""Pruebas del proveedor y webhook Evolution API."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.whatsapp.evolution import EvolutionAPIError, EvolutionWhatsAppProvider
from app.schemas.evolution import (
    extract_message_text,
    extract_phone_from_jid,
    mask_phone,
    normalize_evolution_inbound,
)

FIXTURES = Path(__file__).parent / "fixtures" / "evolution"
client = TestClient(app)


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_mask_phone():
    assert mask_phone("593999888777") == "593****77"
    assert mask_phone("123") == "123"


def test_extract_phone_from_jid():
    assert extract_phone_from_jid("593999888777@s.whatsapp.net") == "593999888777"
    assert extract_phone_from_jid("120363000000000000@g.us") is None
    assert extract_phone_from_jid("status@broadcast") is None


def test_extract_message_text_variants():
    assert extract_message_text({"conversation": " Hola "}) == "Hola"
    assert extract_message_text({"extendedTextMessage": {"text": "Extendido"}}) == "Extendido"
    assert extract_message_text({"imageMessage": {"caption": "x"}}) is None


def test_normalize_valid_inbound():
    payload = _load("messages_upsert_valid.json")
    result = normalize_evolution_inbound(payload)
    assert result is not None
    assert result["provider"] == "evolution"
    assert result["phone"] == "593999888777"
    assert result["message"] == "Quiero solicitar un crédito"
    assert result["message_id"] == "3EB0TEST001"
    assert result["instance"] == "credibot-pruebas"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "messages_upsert_from_me.json",
        "messages_upsert_group.json",
        "messages_upsert_no_text.json",
        "connection_update.json",
    ],
)
def test_normalize_ignored_events(fixture_name):
    assert normalize_evolution_inbound(_load(fixture_name)) is None


@patch("app.providers.whatsapp.evolution.settings.evolution_api_url", "http://evo.test")
@patch("app.providers.whatsapp.evolution.settings.evolution_api_key", "test-key")
@patch("app.providers.whatsapp.evolution.settings.evolution_instance", "credibot-pruebas")
@patch("app.providers.whatsapp.evolution.settings.evolution_timeout_seconds", 5)
@patch("app.providers.whatsapp.evolution.settings.evolution_max_retries", 1)
def test_send_text_success():
    provider = EvolutionWhatsAppProvider()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"key":{"id":"sent-1"}}'
    mock_response.json.return_value = {"key": {"id": "sent-1"}}

    with patch("httpx.request", return_value=mock_response) as mock_request:
        result = provider.send_text("593999888777", "Hola")

    assert result["key"]["id"] == "sent-1"
    mock_request.assert_called_once()
    call_kwargs = mock_request.call_args.kwargs
    assert call_kwargs["json"] == {"number": "593999888777", "text": "Hola"}
    assert call_kwargs["headers"]["apikey"] == "test-key"


@patch("app.providers.whatsapp.evolution.settings.evolution_api_url", "http://evo.test")
@patch("app.providers.whatsapp.evolution.settings.evolution_api_key", "bad-key")
@patch("app.providers.whatsapp.evolution.settings.evolution_instance", "credibot-pruebas")
@patch("app.providers.whatsapp.evolution.settings.evolution_timeout_seconds", 5)
@patch("app.providers.whatsapp.evolution.settings.evolution_max_retries", 0)
def test_send_text_invalid_api_key():
    provider = EvolutionWhatsAppProvider()
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch("httpx.request", return_value=mock_response):
        with pytest.raises(EvolutionAPIError) as exc:
            provider.send_text("593999888777", "Hola")

    assert exc.value.status_code == 401
    assert exc.value.retryable is False


@patch("app.providers.whatsapp.evolution.settings.evolution_api_url", "http://evo.test")
@patch("app.providers.whatsapp.evolution.settings.evolution_api_key", "test-key")
@patch("app.providers.whatsapp.evolution.settings.evolution_instance", "credibot-pruebas")
@patch("app.providers.whatsapp.evolution.settings.evolution_timeout_seconds", 5)
@patch("app.providers.whatsapp.evolution.settings.evolution_max_retries", 1)
def test_send_text_retries_on_5xx():
    provider = EvolutionWhatsAppProvider()
    fail = MagicMock(status_code=503, text="Unavailable", content=b"")
    ok = MagicMock(status_code=200, content=b'{"status":"ok"}', json=lambda: {"status": "ok"})

    with patch("httpx.request", side_effect=[fail, ok]) as mock_request:
        result = provider.send_text("593999888777", "Hola")

    assert result["status"] == "ok"
    assert mock_request.call_count == 2


@patch("app.core.config.settings.evolution_webhook_secret", "lab-secret")
def test_webhook_rejects_invalid_secret():
    payload = _load("messages_upsert_valid.json")
    response = client.post("/webhook/evolution", json=payload)
    assert response.status_code == 403


@patch("app.core.config.settings.evolution_webhook_secret", "lab-secret")
@patch("app.api.routes_webhook._process_inbound")
def test_webhook_accepts_valid_secret_and_processes(mock_process):
    payload = _load("messages_upsert_valid.json")
    response = client.post(
        "/webhook/evolution?secret=lab-secret",
        json=payload,
    )
    assert response.status_code == 200
    mock_process.assert_called_once()
    incoming = mock_process.call_args.args[0]
    assert incoming["phone"] == "593999888777"


@patch("app.core.config.settings.evolution_webhook_secret", "")
@patch("app.api.routes_webhook._process_inbound")
def test_webhook_ignores_non_text_events(mock_process):
    payload = _load("messages_upsert_from_me.json")
    response = client.post("/webhook/evolution", json=payload)
    assert response.status_code == 200
    mock_process.assert_not_called()


@patch("app.core.config.settings.evolution_webhook_secret", "")
@patch("app.api.routes_webhook.inbound_events_repository.try_claim_event", return_value=False)
@patch("app.api.routes_webhook.process_message")
def test_webhook_duplicate_skips_processing(mock_process_message, mock_claim):
    payload = _load("messages_upsert_valid.json")
    response = client.post("/webhook/evolution", json=payload)
    assert response.status_code == 200
    mock_claim.assert_called_once()
    mock_process_message.assert_not_called()


@patch("app.core.config.settings.whatsapp_provider", "evolution")
@patch("app.providers.whatsapp.evolution.settings.evolution_api_url", "http://evo.test")
@patch("app.providers.whatsapp.evolution.settings.evolution_api_key", "test-key")
@patch("app.providers.whatsapp.evolution.settings.evolution_instance", "credibot-pruebas")
def test_evolution_health_endpoint():
    provider_response = {"instance": {"state": "open"}}
    mock_response = MagicMock(status_code=200, content=b"{}", json=lambda: provider_response)
    with patch("httpx.request", return_value=mock_response):
        response = client.get("/health/evolution")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_factory_returns_evolution_provider():
    with patch("app.providers.whatsapp.factory.settings.whatsapp_provider", "evolution"):
        from app.providers.whatsapp.factory import get_whatsapp_provider

        provider = get_whatsapp_provider()
        assert provider.name == "evolution"
