"""Rutas del simulador para probar el bot sin Twilio."""
from fastapi import APIRouter

from app.repositories import conversation_repository, user_repository
from app.schemas.conversation import SimulateMessageRequest, SimulateMessageResponse
from app.services.conversation_service import get_last_agent_metadata, process_message

router = APIRouter(prefix="/simulate", tags=["simulator"])


@router.post("/message", response_model=SimulateMessageResponse)
def simulate_message(payload: SimulateMessageRequest):
    """Endpoint para simular un mensaje entrante y obtener la respuesta del bot."""
    reply = process_message(payload.phone, payload.message)
    state = None
    agent_mode = None
    tokens = None
    latency_ms = None
    model = None
    try:
        user = user_repository.get_user_by_phone(payload.phone)
        if user:
            conversation = conversation_repository.get_active_conversation(user["id"])
            if conversation:
                state = conversation.get("current_state")
                meta = get_last_agent_metadata(conversation["id"])
                agent_mode = meta.get("mode")
                tokens = meta.get("tokens")
                latency_ms = meta.get("latency_ms")
                model = meta.get("model")
    except Exception:
        pass
    return SimulateMessageResponse(
        phone=payload.phone,
        reply=reply,
        state=state,
        agent_mode=agent_mode,
        tokens=tokens,
        latency_ms=latency_ms,
        model=model,
    )
