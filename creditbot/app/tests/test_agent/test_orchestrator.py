"""Pruebas del orquestador GPT."""
from app.agent.orchestrator import AgentOrchestrator


def test_orchestrator_deterministic_when_gpt_disabled():
    orchestrator = AgentOrchestrator()
    result = orchestrator.process(
        user_message="hola",
        state="MENU",
        canonical_response="Respuesta canónica",
    )
    assert result["mode"] == "deterministic"
    assert result["content"] == "Respuesta canónica"
