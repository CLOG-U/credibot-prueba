"""Orquestador GPT con tools, guardrails y fallback determinista."""
import json
from typing import Any

from app.agent.context_builder import ConversationContextBuilder
from app.agent.guardrails import detect_prompt_injection, validate_agent_output
from app.agent.prompts import NO_INVENTION_RULES, SYSTEM_PROMPT
from app.core.config import settings
from app.providers.openai_client import get_llm_provider
from app.tools.registry import execute_tool, get_openai_tool_schemas


class AgentOrchestrator:
    """Coordina conversación GPT + tools con guardrails."""

    def __init__(self) -> None:
        self._provider = get_llm_provider()
        self._max_iterations = settings.openai_max_iterations
        self._context_builder = ConversationContextBuilder()

    def _build_messages(
        self,
        user_message: str,
        state: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        context_text = json.dumps(context or {}, ensure_ascii=False)[:3000]
        return [
            {"role": "system", "content": SYSTEM_PROMPT + NO_INVENTION_RULES},
            {
                "role": "user",
                "content": (
                    f"Estado: {state}. Dato esperado: {context.get('expected_input', '') if context else ''}.\n"
                    f"Respuesta canónica (no alterar datos): {context.get('canonical_response', '') if context else ''}.\n"
                    f"Contexto: {context_text}\n"
                    f"Mensaje usuario: {user_message}"
                ),
            },
        ]

    def process(
        self,
        user_message: str,
        state: str,
        conversation_id: str | None = None,
        context: dict[str, Any] | None = None,
        canonical_response: str = "",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Procesa mensaje con GPT o retorna modo determinista/fallback."""
        if detect_prompt_injection(user_message):
            return {
                "mode": "fallback",
                "content": canonical_response,
                "tool_results": [],
                "reason": "prompt_injection",
                "tokens": 0,
            }

        if not settings.enable_gpt_agent:
            return {
                "mode": "deterministic",
                "content": canonical_response,
                "tool_results": [],
                "tokens": 0,
            }

        if not context:
            context = self._context_builder.build(
                conversation_id=conversation_id or "",
                state=state,
                user_id=user_id or "",
                canonical_response=canonical_response,
            )

        messages = self._build_messages(user_message, state, context)
        tools = get_openai_tool_schemas(state)
        tool_results: list[dict[str, Any]] = []
        total_tokens = 0

        try:
            for _ in range(self._max_iterations):
                response = self._provider.chat_completion(messages, tools)
                total_tokens += response.get("usage", {}).get("total_tokens", 0)

                if response.get("tool_calls"):
                    for call in response["tool_calls"]:
                        args = json.loads(call["arguments"]) if call["arguments"] else {}
                        if call["name"] == "derivar_a_asesor" and user_id and conversation_id:
                            args.setdefault("user_id", user_id)
                            args.setdefault("conversation_id", conversation_id)
                        result = execute_tool(
                            call["name"],
                            args,
                            conversation_id=conversation_id,
                            state=state,
                        )
                        tool_results.append({"tool": call["name"], "result": result.to_dict()})
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

                content = response.get("content", "").strip()
                validation_error = validate_agent_output(content, tool_results, canonical_response)
                if validation_error:
                    return {
                        "mode": "fallback",
                        "content": canonical_response,
                        "tool_results": tool_results,
                        "reason": validation_error,
                        "tokens": total_tokens,
                    }

                final_content = content or canonical_response
                return {
                    "mode": "gpt",
                    "content": final_content,
                    "tool_results": tool_results,
                    "tokens": total_tokens,
                }

        except Exception as exc:
            return {
                "mode": "fallback",
                "content": canonical_response,
                "tool_results": tool_results,
                "reason": str(exc),
                "tokens": total_tokens,
            }

        return {
            "mode": "fallback",
            "content": canonical_response,
            "tool_results": tool_results,
            "reason": "max_iterations",
            "tokens": total_tokens,
        }
