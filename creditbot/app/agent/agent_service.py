"""Servicio singleton del agente GPT."""
from functools import lru_cache

from app.agent.orchestrator import AgentOrchestrator


@lru_cache
def get_agent_orchestrator() -> AgentOrchestrator:
    """Retorna instancia única del orquestador."""
    return AgentOrchestrator()
