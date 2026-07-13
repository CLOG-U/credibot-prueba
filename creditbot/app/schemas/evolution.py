"""Normalización de webhooks Evolution API al modelo interno de CrediBot."""
from typing import Any

SUPPORTED_INBOUND_EVENTS = {"messages.upsert", "messages_upsert"}


def mask_phone(phone: str) -> str:
    """Enmascara teléfono para logs: 593****99."""
    cleaned = phone.replace("+", "").strip()
    if len(cleaned) <= 5:
        return cleaned
    return f"{cleaned[:3]}****{cleaned[-2:]}"


def _normalize_event_name(event: str | None) -> str:
    return (event or "").strip().lower().replace(".", "_")


def extract_phone_from_jid(remote_jid: str | None) -> str | None:
    """Extrae dígitos del JID; retorna None para grupos o broadcast."""
    if not remote_jid:
        return None
    jid = remote_jid.lower()
    if "@g.us" in jid or "@broadcast" in jid or "@newsletter" in jid:
        return None
    local_part = jid.split("@", 1)[0]
    if ":" in local_part:
        local_part = local_part.split(":", 1)[0]
    digits = "".join(char for char in local_part if char.isdigit())
    return digits or None


def extract_message_text(message_obj: dict[str, Any] | None) -> str | None:
    """Extrae texto plano de un objeto message de Baileys."""
    if not message_obj:
        return None

    conversation = message_obj.get("conversation")
    if isinstance(conversation, str) and conversation.strip():
        return conversation.strip()

    extended = message_obj.get("extendedTextMessage") or {}
    extended_text = extended.get("text")
    if isinstance(extended_text, str) and extended_text.strip():
        return extended_text.strip()

    ephemeral = message_obj.get("ephemeralMessage") or {}
    nested = ephemeral.get("message")
    if isinstance(nested, dict):
        return extract_message_text(nested)

    return None


def _unwrap_message_data(data: Any) -> dict[str, Any] | None:
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                return item
    return None


def normalize_evolution_inbound(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    Normaliza MESSAGES_UPSERT al contrato interno.
    Retorna None si el evento debe ignorarse.
    """
    event = _normalize_event_name(payload.get("event"))
    if event not in SUPPORTED_INBOUND_EVENTS:
        return None

    data = _unwrap_message_data(payload.get("data"))
    if not data:
        return None

    key = data.get("key") or {}
    if key.get("fromMe") is True:
        return None

    remote_jid = key.get("remoteJid") or key.get("remote_jid")
    phone = extract_phone_from_jid(remote_jid)
    if not phone:
        return None

    text = extract_message_text(data.get("message"))
    if not text:
        return None

    message_id = key.get("id")
    instance = payload.get("instance") or payload.get("instanceName")
    timestamp = data.get("messageTimestamp") or payload.get("date_time")

    return {
        "provider": "evolution",
        "instance": instance,
        "phone": phone,
        "message": text,
        "message_id": message_id,
        "type": "text",
        "timestamp": timestamp,
        "raw_payload": payload,
    }
