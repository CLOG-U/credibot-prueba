"""Interfaz base de proveedores WhatsApp."""
from typing import Any, Protocol


class WhatsAppProvider(Protocol):
    """Contrato para enviar mensajes y validar webhooks."""

    name: str

    def send_text(self, to_phone: str, message: str) -> dict[str, Any]: ...

    def parse_inbound(self, payload: dict[str, Any]) -> dict[str, Any] | None: ...
