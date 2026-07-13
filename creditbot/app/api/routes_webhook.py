"""Rutas del webhook de WhatsApp (Twilio y Meta)."""
import logging

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.core.config import settings
from app.providers.whatsapp.factory import get_whatsapp_provider
from app.providers.whatsapp.meta_cloud import MetaWhatsAppProvider
from app.repositories import inbound_events_repository
from app.schemas.whatsapp import extract_twilio_message
from app.services.conversation_service import process_message
from app.services.whatsapp_service import WhatsAppServiceError
from app.session.session_store import sync_session_from_conversation
from app.repositories import conversation_repository, user_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["whatsapp"])


def _validate_twilio_signature(request: Request, form_data: dict[str, str]) -> None:
    """Valida la firma X-Twilio-Signature si la configuración lo requiere."""
    if not settings.twilio_validate_signature:
        return

    if not settings.app_public_url:
        raise HTTPException(
            status_code=500,
            detail="APP_PUBLIC_URL es requerido para validar la firma de Twilio.",
        )

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        raise HTTPException(status_code=403, detail="Falta la firma de Twilio.")

    try:
        from twilio.request_validator import RequestValidator
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Instala el paquete twilio para validar firmas.",
        ) from exc

    url = f"{settings.app_public_url.rstrip('/')}{request.url.path}"
    validator = RequestValidator(settings.twilio_auth_token)
    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Firma de Twilio inválida.")


@router.get("/whatsapp")
def whatsapp_webhook_verify(
    request: Request,
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    """Verificación GET para Meta o estado para Twilio."""
    if hub_mode == "subscribe":
        if hub_verify_token != settings.meta_verify_token:
            raise HTTPException(status_code=403, detail="Token de verificación inválido")
        return Response(content=hub_challenge or "", media_type="text/plain")

    provider = get_whatsapp_provider()
    return {
        "status": "ok",
        "provider": provider.name,
        "message": "Webhook activo para WhatsApp.",
    }


async def _process_inbound(incoming: dict) -> None:
    """Procesa mensaje entrante con idempotencia y sesión."""
    provider_name = incoming.get("provider", settings.whatsapp_provider)
    message_id = incoming.get("message_id")
    phone = incoming["phone"]
    message = incoming["message"]
    raw_payload = incoming.get("raw_payload")

    if message_id:
        claimed = inbound_events_repository.try_claim_event(
            provider_name,
            message_id,
            phone=phone,
            payload=raw_payload,
        )
        if not claimed:
            logger.info("Mensaje duplicado descartado: %s", message_id)
            return

    reply = process_message(phone, message, raw_payload=raw_payload)

    try:
        user = user_repository.get_or_create_user(phone)
        conversation = conversation_repository.get_or_create_active_conversation(user["id"])
        sync_session_from_conversation(conversation)
    except Exception:
        pass

    provider = get_whatsapp_provider()
    try:
        provider.send_text(phone, reply)
    except (WhatsAppServiceError, ValueError) as exc:
        logger.error("No se pudo enviar mensaje a %s: %s", phone, exc)


@router.post("/whatsapp")
async def receive_whatsapp_webhook(request: Request):
    """Recibe mensajes de Twilio o Meta."""
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        raw_body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not MetaWhatsAppProvider.validate_signature(raw_body, signature):
            raise HTTPException(status_code=403, detail="Firma Meta inválida")

        payload = await request.json()
        provider = MetaWhatsAppProvider()
        incoming = provider.parse_inbound(payload)
        if incoming:
            await _process_inbound(incoming)
        return {"status": "ok"}

    form = await request.form()
    form_data = {key: str(value) for key, value in form.items()}
    _validate_twilio_signature(request, form_data)

    incoming = extract_twilio_message(
        form_data.get("From", ""),
        form_data.get("Body", ""),
        form_data.get("MessageSid") or None,
    )
    if incoming:
        incoming["provider"] = "twilio"
        incoming["message_id"] = incoming.get("message_id") or form_data.get("MessageSid")
        await _process_inbound(incoming)

    return Response(content="", media_type="text/plain")
