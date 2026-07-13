"""Ruta de health check para monitoreo."""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Endpoint de verificación de estado del servicio."""
    return {"status": "ok", "app": "CrediBot", "whatsapp_provider": settings.whatsapp_provider}


@router.get("/health/evolution")
def evolution_health_check():
    """Health check opcional de la instancia Evolution (EVO-12)."""
    if settings.whatsapp_provider.lower() != "evolution":
        return {"status": "skipped", "reason": "WHATSAPP_PROVIDER no es evolution"}

    from app.providers.whatsapp.evolution import EvolutionAPIError, EvolutionWhatsAppProvider

    provider = EvolutionWhatsAppProvider()
    try:
        state = provider.get_connection_state()
        return {
            "status": "ok",
            "instance": settings.evolution_instance,
            "connection": state,
        }
    except EvolutionAPIError as exc:
        return {
            "status": "error",
            "instance": settings.evolution_instance,
            "error": str(exc),
            "retryable": exc.retryable,
        }
