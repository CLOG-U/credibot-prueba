"""Proveedor Meta WhatsApp Cloud API."""
import hashlib
import hmac
from typing import Any

import httpx

from app.core.config import settings


class MetaWhatsAppProvider:
    name = "meta"

    def _api_url(self) -> str:
        if not settings.meta_phone_number_id:
            raise ValueError("META_PHONE_NUMBER_ID no configurado")
        return f"https://graph.facebook.com/v19.0/{settings.meta_phone_number_id}/messages"

    def send_text(self, to_phone: str, message: str) -> dict[str, Any]:
        if not settings.meta_access_token:
            raise ValueError("META_ACCESS_TOKEN no configurado")

        phone = to_phone.replace("+", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message},
        }
        response = httpx.post(
            self._api_url(),
            headers={"Authorization": f"Bearer {settings.meta_access_token}"},
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def parse_inbound(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        try:
            entry = payload["entry"][0]
            change = entry["changes"][0]
            value = change["value"]
            message = value["messages"][0]
            phone = message["from"]
            text = message.get("text", {}).get("body", "")
            message_id = message.get("id")
            return {
                "phone": phone,
                "message": text,
                "message_id": message_id,
                "provider": self.name,
                "raw_payload": payload,
            }
        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def validate_signature(raw_body: bytes, signature_header: str) -> bool:
        """Valida X-Hub-Signature-256 de Meta."""
        if not settings.meta_app_secret:
            return True
        if not signature_header.startswith("sha256="):
            return False
        expected = signature_header.split("=", 1)[1]
        digest = hmac.new(
            settings.meta_app_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(digest, expected)
