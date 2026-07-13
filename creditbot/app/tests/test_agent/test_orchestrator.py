"""Pruebas del orquestador GPT."""
from unittest.mock import patch

from app.agent.orchestrator import AgentOrchestrator


def test_orchestrator_deterministic_when_gpt_disabled():
    orchestrator = AgentOrchestrator()
    with patch("app.agent.orchestrator.settings.enable_gpt_agent", False):
        result = orchestrator.process(
            user_message="hola",
            state="MENU",
            canonical_response="Respuesta canónica",
        )
    assert result["mode"] == "deterministic"
    assert result["content"] == "Respuesta canónica"
