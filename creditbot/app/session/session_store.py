"""Almacén de sesión con Redis y fallback a Supabase."""
import json
from typing import Any, Protocol

from app.core.config import settings


class SessionStore(Protocol):
    """Interfaz de sesión activa."""

    def get(self, conversation_id: str) -> dict[str, Any] | None: ...
    def set(self, conversation_id: str, data: dict[str, Any], ttl_seconds: int = 3600) -> None: ...
    def delete(self, conversation_id: str) -> None: ...


class InMemorySessionStore:
    """Fallback en memoria cuando Redis no está disponible."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def get(self, conversation_id: str) -> dict[str, Any] | None:
        return self._data.get(conversation_id)

    def set(self, conversation_id: str, data: dict[str, Any], ttl_seconds: int = 3600) -> None:
        self._data[conversation_id] = data

    def delete(self, conversation_id: str) -> None:
        self._data.pop(conversation_id, None)


class RedisSessionStore:
    """Sesión en Redis con TTL."""

    def __init__(self, url: str) -> None:
        import redis

        self._client = redis.from_url(url, decode_responses=True)

    def _key(self, conversation_id: str) -> str:
        return f"credibot:session:{conversation_id}"

    def get(self, conversation_id: str) -> dict[str, Any] | None:
        raw = self._client.get(self._key(conversation_id))
        if not raw:
            return None
        return json.loads(raw)

    def set(self, conversation_id: str, data: dict[str, Any], ttl_seconds: int = 3600) -> None:
        self._client.setex(self._key(conversation_id), ttl_seconds, json.dumps(data))

    def delete(self, conversation_id: str) -> None:
        self._client.delete(self._key(conversation_id))


_session_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    """Retorna Redis si está configurado; si no, memoria."""
    global _session_store
    if _session_store is not None:
        return _session_store

    if settings.redis_url:
        try:
            _session_store = RedisSessionStore(settings.redis_url)
            return _session_store
        except Exception:
            pass

    _session_store = InMemorySessionStore()
    return _session_store


def load_session_from_supabase(conversation_id: str) -> dict[str, Any] | None:
    """Recupera sesión desde Supabase cuando no hay caché."""
    try:
        from app.repositories import message_repository
        from app.repositories.supabase_client import get_supabase_client

        conv = (
            get_supabase_client()
            .table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .limit(1)
            .execute()
        )
        if not conv.data:
            return None

        conversation = conv.data[0]
        messages = message_repository.get_messages_by_conversation(conversation_id)
        session_data = {
            "state": conversation.get("current_state"),
            "validation_failures": conversation.get("validation_failures", 0),
            "user_id": conversation.get("user_id"),
            "message_count": len(messages),
            "recovered_from": "supabase",
        }
        get_session_store().set(conversation_id, session_data)
        return session_data
    except Exception:
        return None


def sync_session_from_conversation(conversation: dict[str, Any]) -> None:
    """Sincroniza estado de conversación Supabase hacia sesión."""
    get_session_store().set(
        conversation["id"],
        {
            "state": conversation.get("current_state"),
            "validation_failures": conversation.get("validation_failures", 0),
            "user_id": conversation.get("user_id"),
            "recovered_from": "live",
        },
    )


def get_or_recover_session(conversation_id: str) -> dict[str, Any] | None:
    """Obtiene sesión de caché o recupera desde Supabase."""
    store = get_session_store()
    data = store.get(conversation_id)
    if data:
        return data
    return load_session_from_supabase(conversation_id)
