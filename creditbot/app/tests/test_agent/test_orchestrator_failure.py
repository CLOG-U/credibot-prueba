"""Pruebas extendidas del orquestador."""
from unittest.mock import patch

from app.agent.orchestrator import AgentOrchestrator


def test_orchestrator_fallback_when_provider_raises():
    orchestrator = AgentOrchestrator()

    class FailingProvider:
        def chat_completion(self, messages, tools=None):
            raise TimeoutError("openai timeout")

    orchestrator._provider = FailingProvider()
    with patch("app.agent.orchestrator.settings.enable_gpt_agent", True):
        result = orchestrator.process(
            user_message="hola",
            state="MENU",
            canonical_response="Respuesta canónica",
            context={"canonical_response": "Respuesta canónica", "expected_input": "menu"},
        )

    assert result["mode"] == "fallback"
    assert result["content"] == "Respuesta canónica"
    assert "timeout" in result["reason"].lower()
    assert result["latency_ms"] >= 0
