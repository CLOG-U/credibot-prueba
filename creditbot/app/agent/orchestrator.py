"""Orquestador GPT con tools y fallback determinista."""
import json
import re
from typing import Any

from app.agent.prompts import NO_INVENTION_RULES, SYSTEM_PROMPT
from app.core.config import settings
from app.providers.openai_client import get_llm_provider
from app.tools.registry import execute_tool, get_openai_tool_schemas

FORBIDDEN_PATTERNS = [
    r"score\s*(de\s*)?\d{3}",
    r"\$\s*\d+[\d,.]*",
    r"preaprobado|observado|no_cumple",
]


class AgentOrchestrator:
    """Coordina conversación GPT + tools con guardrails."""

    def __init__(self) -> None:
        self._provider = get_llm_provider()
        self._max_iterations = settings.openai_max_iterations

    def _build_messages(
        self,
        user_message: str,
        state: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        context_text = ""
        if context:
            context_text = f"\nContexto: estado={state}, datos={json.dumps(context, ensure_ascii=False)}"
        return [
            {"role": "system", "content": SYSTEM_PROMPT + NO_INVENTION_RULES},
            {
                "role": "user",
                "content": f"Estado actual: {state}.{context_text}\nMensaje: {user_message}",
            },
        ]

    def _validate_response(self, content: str, used_tools: bool) -> str | None:
        """Rechaza respuestas que parecen inventar datos crediticios."""
        if used_tools:
            return None
        lowered = content.lower()
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, lowered):
                return "invalid_invented_data"
        return None

    def process(
        self,
        user_message: str,
        state: str,
        conversation_id: str | None = None,
        context: dict[str, Any] | None = None,
        fallback_handler=None,
    ) -> dict[str, Any]:
        """
        Procesa mensaje con GPT. Si falla o está deshabilitado, usa fallback.
        """
        if not settings.enable_gpt_agent:
            if fallback_handler:
                return {
                    "mode": "deterministic",
                    "content": fallback_handler(user_message),
                    "tool_results": [],
                }
            return {"mode": "disabled", "content": "", "tool_results": []}

        messages = self._build_messages(user_message, state, context)
        tools = get_openai_tool_schemas()
        tool_results: list[dict[str, Any]] = []
        total_tokens = 0

        try:
            for _ in range(self._max_iterations):
                response = self._provider.chat_completion(messages, tools)
                total_tokens += response.get("usage", {}).get("total_tokens", 0)

                if response.get("tool_calls"):
                    for call in response["tool_calls"]:
                        args = json.loads(call["arguments"]) if call["arguments"] else {}
                        result = execute_tool(
                            call["name"],
                            args,
                            conversation_id=conversation_id,
                            state=state,
                        )
                        tool_results.append(
                            {"tool": call["name"], "result": result.to_dict()}
                        )
                        messages.append(
                            {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": call["id"],
                                        "type": "function",
                                        "function": {
                                            "name": call["name"],
                                            "arguments": call["arguments"],
                                        },
                                    }
                                ],
                            }
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "content": json.dumps(result.to_dict(), ensure_ascii=False),
                            }
                        )
                    continue

                content = response.get("content", "")
                validation_error = self._validate_response(content, bool(tool_results))
                if validation_error and fallback_handler:
                    return {
                        "mode": "fallback",
                        "content": fallback_handler(user_message),
                        "tool_results": tool_results,
                        "reason": validation_error,
                        "tokens": total_tokens,
                    }

                return {
                    "mode": "gpt",
                    "content": content,
                    "tool_results": tool_results,
                    "tokens": total_tokens,
                }

        except Exception as exc:
            if fallback_handler:
                return {
                    "mode": "fallback",
                    "content": fallback_handler(user_message),
                    "tool_results": tool_results,
                    "reason": str(exc),
                    "tokens": total_tokens,
                }
            return {
                "mode": "error",
                "content": "No pude procesar tu mensaje. Intenta de nuevo.",
                "tool_results": tool_results,
                "reason": str(exc),
                "tokens": total_tokens,
            }

        if fallback_handler:
            return {
                "mode": "fallback",
                "content": fallback_handler(user_message),
                "tool_results": tool_results,
                "reason": "max_iterations",
                "tokens": total_tokens,
            }
        return {"mode": "error", "content": "", "tool_results": tool_results}
