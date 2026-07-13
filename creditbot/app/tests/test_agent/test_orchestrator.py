"""Pruebas del orquestador GPT."""
from app.agent.orchestrator import AgentOrchestrator


def test_orchestrator_fallback_when_gpt_disabled():
    orchestrator = AgentOrchestrator()

    def fallback(msg):
        return f"fallback:{msg}"

    result = orchestrator.process(
        user_message="hola",
        state="MENU",
        fallback_handler=fallback,
    )
    assert result["mode"] == "deterministic"
    assert "fallback:hola" in result["content"]
