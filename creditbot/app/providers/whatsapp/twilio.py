"""Proveedor WhatsApp Twilio."""
from typing import Any

from app.services import whatsapp_service


class TwilioWhatsAppProvider:
    name = "twilio"

    def send_text(self, to_phone: str, message: str) -> dict[str, Any]:
        return whatsapp_service.send_text_message(to_phone, message)

    def parse_inbound(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        from app.schemas.whatsapp import extract_twilio_message

        return extract_twilio_message(
            payload.get("From", ""),
            payload.get("Body", ""),
            payload.get("MessageSid"),
        )
