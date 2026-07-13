"""Factory de proveedor WhatsApp."""
from app.core.config import settings
from app.providers.whatsapp.evolution import EvolutionWhatsAppProvider
from app.providers.whatsapp.meta_cloud import MetaWhatsAppProvider
from app.providers.whatsapp.twilio import TwilioWhatsAppProvider


def get_whatsapp_provider():
    """Retorna proveedor según WHATSAPP_PROVIDER."""
    provider = settings.whatsapp_provider.lower()
    if provider == "meta":
        return MetaWhatsAppProvider()
    if provider == "evolution":
        return EvolutionWhatsAppProvider()
    return TwilioWhatsAppProvider()
