"""Repositorio de perfiles crediticios ficticios."""
from typing import Any

from app.repositories.supabase_client import get_supabase_client


def get_profile_by_cedula(cedula: str) -> dict[str, Any] | None:
    """Busca un perfil crediticio por cédula."""
    response = (
        get_supabase_client()
        .table("credit_profiles")
        .select("*")
        .eq("cedula", cedula)
        .limit(1)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None
