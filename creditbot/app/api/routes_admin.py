"""Rutas administrativas para consultar datos del sistema."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import verify_admin_password
from app.domain.cedula_validator import mask_cedula
from app.repositories import conversation_repository, message_repository, user_repository
from app.repositories.supabase_client import get_supabase_client
from app.services.handoff_service import get_pending_handoff_cases

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_admin_password)])


def _mask_user(user: dict) -> dict:
    masked = dict(user)
    if masked.get("cedula"):
        masked["cedula"] = mask_cedula(str(masked["cedula"]))
    if masked.get("phone"):
        phone = str(masked["phone"])
        masked["phone"] = f"{phone[:3]}****{phone[-2:]}" if len(phone) > 5 else phone
    return masked


@router.get("/requests")
def list_credit_requests():
    """Retorna solicitudes de crédito con datos enmascarados."""
    response = (
        get_supabase_client()
        .table("credit_requests")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    items = []
    for row in response.data or []:
        item = dict(row)
        if item.get("cedula"):
            item["cedula"] = mask_cedula(str(item["cedula"]))
        items.append(item)
    return {"items": items}


@router.get("/handoff")
def list_handoff_cases():
    """Retorna los casos de derivación pendientes."""
    return {"items": get_pending_handoff_cases()}


@router.get("/audit/tools")
def list_tool_audit_logs(limit: int = 50):
    """Retorna auditoría reciente de tools."""
    response = (
        get_supabase_client()
        .table("tool_audit_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return {"items": response.data or []}


@router.get("/conversations/{phone}")
def get_conversation_by_phone(phone: str):
    """Retorna usuario, conversación y mensajes dado un número de teléfono."""
    user = user_repository.get_user_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    conversation = conversation_repository.get_active_conversation(user["id"])
    if not conversation:
        response = (
            get_supabase_client()
            .table("conversations")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if response.data:
            conversation = response.data[0]

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada.")

    messages = message_repository.get_messages_by_conversation(conversation["id"])
    return {
        "user": _mask_user(user),
        "conversation": conversation,
        "messages": messages,
    }
