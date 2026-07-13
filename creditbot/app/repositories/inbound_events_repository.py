"""Idempotencia de eventos entrantes de webhooks."""
from typing import Any

from app.repositories.supabase_client import get_supabase_client


def is_duplicate_event(provider: str, external_message_id: str) -> bool:
    """Verifica si el mensaje ya fue procesado."""
    if not external_message_id:
        return False
    response = (
        get_supabase_client()
        .table("inbound_events")
        .select("id")
        .eq("provider", provider)
        .eq("external_message_id", external_message_id)
        .limit(1)
        .execute()
    )
    return bool(response.data)


def try_claim_event(
    provider: str,
    external_message_id: str,
    phone: str | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """
    Reserva el evento antes de procesarlo.
    Retorna True si este worker puede procesarlo; False si ya fue reclamado.
    """
    if not external_message_id:
        return True

    if is_duplicate_event(provider, external_message_id):
        return False

    try:
        get_supabase_client().table("inbound_events").insert(
            {
                "provider": provider,
                "external_message_id": external_message_id,
                "phone": phone,
                "payload": payload,
            }
        ).execute()
        return True
    except Exception:
        return False


def register_event(
    provider: str,
    external_message_id: str,
    phone: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Registra mensaje procesado (compatibilidad)."""
    try_claim_event(provider, external_message_id, phone=phone, payload=payload)
