"""Proveedor WhatsApp Evolution API (Baileys)."""
import logging
import time
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.evolution import mask_phone, normalize_evolution_inbound

logger = logging.getLogger(__name__)


class EvolutionAPIError(Exception):
    """Error tipado al comunicarse con Evolution API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class EvolutionWhatsAppProvider:
    """Adaptador Evolution API detrás de WhatsAppProvider."""

    name = "evolution"

    def _base_url(self) -> str:
        if not settings.evolution_api_url:
            raise EvolutionAPIError("EVOLUTION_API_URL no configurado")
        return settings.evolution_api_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not settings.evolution_api_key:
            raise EvolutionAPIError("EVOLUTION_API_KEY no configurado")
        return {
            "apikey": settings.evolution_api_key,
            "Content-Type": "application/json",
        }

    def _instance(self) -> str:
        if not settings.evolution_instance:
            raise EvolutionAPIError("EVOLUTION_INSTANCE no configurado")
        return settings.evolution_instance

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url()}{path}"
        timeout = settings.evolution_timeout_seconds
        max_retries = max(settings.evolution_max_retries, 0)
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                response = httpx.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=json,
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                last_error = EvolutionAPIError(
                    f"Timeout al contactar Evolution API ({timeout}s)",
                    retryable=True,
                )
                if attempt >= max_retries:
                    raise last_error from exc
                time.sleep(0.5 * (attempt + 1))
                continue
            except httpx.RequestError as exc:
                last_error = EvolutionAPIError(
                    f"Error de conexión con Evolution API: {exc}",
                    retryable=True,
                )
                if attempt >= max_retries:
                    raise last_error from exc
                time.sleep(0.5 * (attempt + 1))
                continue

            if response.status_code >= 500:
                last_error = EvolutionAPIError(
                    f"Evolution API error {response.status_code}",
                    status_code=response.status_code,
                    retryable=True,
                )
                if attempt >= max_retries:
                    raise last_error
                time.sleep(0.5 * (attempt + 1))
                continue

            if response.status_code >= 400:
                raise EvolutionAPIError(
                    f"Evolution API error {response.status_code}: {response.text[:200]}",
                    status_code=response.status_code,
                    retryable=False,
                )

            if not response.content:
                return {}
            return response.json()

        if last_error:
            raise last_error
        raise EvolutionAPIError("Evolution API request failed")

    def send_text(self, to_phone: str, message: str) -> dict[str, Any]:
        phone = to_phone.replace("+", "").strip()
        instance = self._instance()
        logger.info(
            "Enviando mensaje Evolution a %s (instancia %s)",
            mask_phone(phone),
            instance,
        )
        return self._request(
            "POST",
            f"/message/sendText/{instance}",
            json={"number": phone, "text": message},
        )

    def parse_inbound(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        return normalize_evolution_inbound(payload)

    def get_connection_state(self) -> dict[str, Any]:
        """Consulta el estado de conexión de la instancia (EVO-12)."""
        instance = self._instance()
        return self._request("GET", f"/instance/connectionState/{instance}")

    @staticmethod
    def validate_webhook_secret(
        query_secret: str | None,
        header_secret: str | None,
    ) -> bool:
        """Valida el secreto del webhook si está configurado."""
        expected = settings.evolution_webhook_secret
        if not expected:
            return True
        provided = header_secret or query_secret
        if not provided:
            return False
        return provided == expected
