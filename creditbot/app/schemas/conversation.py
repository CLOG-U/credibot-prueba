"""Esquemas Pydantic para el simulador de mensajes."""
from pydantic import BaseModel, Field


class SimulateMessageRequest(BaseModel):
    """Cuerpo de la petición para simular un mensaje entrante."""

    phone: str = Field(..., examples=["593999999999"])
    message: str = Field(..., examples=["Hola"])


class SimulateMessageResponse(BaseModel):
    """Respuesta del simulador con metadata v3."""

    phone: str
    reply: str
    state: str | None = None
    agent_mode: str | None = None
    tokens: int | None = None
    latency_ms: int | None = None
    model: str | None = None
