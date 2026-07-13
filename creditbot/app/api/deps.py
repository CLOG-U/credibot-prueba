"""Autenticación básica para endpoints administrativos."""
from fastapi import Header, HTTPException

from app.core.config import settings


def verify_admin_password(x_admin_password: str = Header(default="")) -> None:
    """Valida contraseña de administrador."""
    expected = settings.admin_dashboard_password
    if not expected:
        return
    if x_admin_password != expected:
        raise HTTPException(status_code=401, detail="No autorizado")
