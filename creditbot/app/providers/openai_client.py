"""Cliente OpenAI con modo simulado para CI."""
from typing import Any

from app.core.config import settings


class LLMProvider:
    """Abstracción del proveedor LLM."""

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Proveedor simulado para tests y CI."""

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        return {
            "content": f"[modo simulado] Recibí tu mensaje. El flujo determinista continúa.",
            "tool_calls": [],
            "usage": {"total_tokens": 0},
        }


class OpenAIProvider(LLMProvider):
    """Cliente real de OpenAI."""

    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": settings.openai_model,
            "messages": messages,
            "max_tokens": settings.openai_max_tokens,
            "temperature": 0.2,
        }
        if tools:
            kwargs["tools"] = tools

        response = self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        tool_calls = []
        if message.tool_calls:
            for call in message.tool_calls:
                tool_calls.append(
                    {
                        "id": call.id,
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    }
                )

        usage = {"total_tokens": response.usage.total_tokens if response.usage else 0}
        return {
            "content": message.content or "",
            "tool_calls": tool_calls,
            "usage": usage,
        }


def get_llm_provider() -> LLMProvider:
    """Retorna proveedor según configuración."""
    if settings.llm_provider == "mock" or not settings.openai_api_key:
        return MockLLMProvider()
    return OpenAIProvider()
