"""Lógica principal del flujo conversacional v3 (determinista + GPT opcional)."""
import re
from typing import Any

from app.agent.agent_service import get_agent_orchestrator
from app.agent.context_builder import ConversationContextBuilder, get_draft_for_conversation
from app.core.constants import (
    ASK_CEDULA,
    ASK_EMPLOYMENT,
    ASK_EXPENSES,
    ASK_INCOME,
    ASK_PURPOSE,
    ASK_TERM,
    CONFIRM,
    CONSENTIMIENTO,
    CREDIT_RESULT_OBSERVED,
    FINISHED,
    HANDOFF_REQUESTED,
    MAX_VALIDATION_FAILURES,
    MENU,
    NOT_ELIGIBLE,
    SHOW_RESULT,
    START,
)
from app.core.config import settings
from app.domain.cedula_validator import normalize_cedula
from app.domain.credit_rules import (
    RULES_VERSION,
    CreditProfileInput,
    evaluate_eligibility,
    evaluate_precalification,
)
from app.repositories import (
    conversation_repository,
    credit_profile_repository,
    credit_repository,
    message_repository,
    user_repository,
)
from app.services import handoff_service, message_service, nlu_parser, validation_service
from app.session.session_store import get_or_recover_session, sync_session_from_conversation
from app.tools.policy_tools import obtener_politica_credito

HANDOFF_KEYWORDS = {"asesor", "humano", "persona", "agente", "asesora", "operador"}

_pending_evaluations: dict[str, dict[str, Any]] = {}
_context_builder = ConversationContextBuilder()
_last_agent_meta: dict[str, dict[str, Any]] = {}


def get_last_agent_metadata(conversation_id: str) -> dict[str, Any]:
    """Retorna metadata del último procesamiento del agente."""
    return _last_agent_meta.get(conversation_id, {})


def _contains_handoff_keyword(text: str) -> bool:
    """Detecta palabras clave de derivación como palabras completas."""
    return any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in HANDOFF_KEYWORDS)


def _request_handoff(
    conversation_id: str,
    user_id: str,
    response: str,
    reason: str,
    credit_request_id: str | None = None,
) -> str:
    """Deriva la conversación a un asesor humano."""
    handoff_service.register_handoff(
        user_id=user_id,
        conversation_id=conversation_id,
        reason=reason,
        credit_request_id=credit_request_id,
    )
    conversation_repository.reset_validation_failures(conversation_id)
    conversation_repository.update_state(conversation_id, HANDOFF_REQUESTED)
    conversation_repository.update_last_message(conversation_id, response)
    conversation_repository.finish_conversation(conversation_id)
    message_repository.save_outbound_message(conversation_id, user_id, response)
    _pending_evaluations.pop(conversation_id, None)
    return response


def _handle_validation_failure(
    conversation_id: str,
    user_id: str,
    response: str,
) -> str | None:
    """Incrementa fallos y deriva si supera el límite."""
    count = conversation_repository.increment_validation_failures(conversation_id)
    if count >= MAX_VALIDATION_FAILURES:
        return _request_handoff(
            conversation_id,
            user_id,
            message_service.handoff_message(),
            reason="repeated_invalid_input",
        )
    return response


def _profile_to_input(profile: dict[str, Any]) -> CreditProfileInput:
    """Convierte perfil de BD a entrada de reglas."""
    return CreditProfileInput(
        credit_score=int(profile["credit_score"]),
        score_category=str(profile["score_category"]),
        monthly_debt_payment=float(profile.get("monthly_debt_payment") or 0),
        has_delinquency=bool(profile.get("has_delinquency")),
        delinquency_days=int(profile.get("delinquency_days") or 0),
        is_blacklisted=bool(profile.get("is_blacklisted")),
        no_credit_history=bool(profile.get("no_credit_history")),
    )


def _calculate_and_store(
    conversation_id: str,
    request: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """Calcula precalificación y guarda evaluación pendiente."""
    profile_input = _profile_to_input(profile)
    evaluation = evaluate_precalification(
        profile=profile_input,
        monthly_income=float(request["monthly_income"]),
        monthly_expenses=float(request["monthly_expenses"]),
        term_months=int(request["term_months"]),
    )
    result_data = {
        "result": evaluation.result,
        "category": evaluation.category,
        "max_amount": evaluation.max_amount,
        "suggested_amount": evaluation.suggested_amount,
        "term": int(request["term_months"]),
        "annual_rate": evaluation.annual_rate,
        "monthly_payment": evaluation.monthly_payment,
        "payment_capacity": evaluation.payment_capacity,
        "reasons": evaluation.reasons,
        "rules_version": RULES_VERSION,
        "request_id": request["id"],
    }
    _pending_evaluations[conversation_id] = result_data
    return result_data


def _maybe_answer_policy_question(state: str, text: str, canonical: str) -> str:
    """Enriquece respuesta con RAG si el usuario hace una pregunta informativa."""
    if state not in {"MENU", "CONSENTIMIENTO", "ASK_INCOME", "ASK_EMPLOYMENT", "ASK_EXPENSES", "ASK_TERM", "ASK_PURPOSE"}:
        return canonical
    lowered = text.lower()
    if "?" not in text and not any(
        w in lowered for w in ("qué", "que ", "cuál", "cual", "cómo", "como", "plazo", "tasa", "documento", "privacidad")
    ):
        return canonical

    rag = obtener_politica_credito(text)
    if not rag.success:
        return canonical

    sources = ", ".join(rag.data.get("sources", []))
    snippet = rag.data["chunks"][0]["content"][:400] if rag.data.get("chunks") else ""
    return f"{canonical}\n\nInformación de política ({sources}):\n{snippet}"


def _apply_agent_layer(
    *,
    user_message: str,
    state: str,
    conversation_id: str,
    user_id: str,
    canonical_response: str,
    skip_agent: bool,
) -> tuple[str, dict[str, Any]]:
    """Ejecuta GPT sobre respuesta canónica sin alterar el estado."""
    if skip_agent or not canonical_response or not settings.enable_gpt_agent:
        meta = {"mode": "deterministic", "tokens": 0}
        _last_agent_meta[conversation_id] = meta
        return canonical_response, meta

    draft = get_draft_for_conversation(conversation_id)
    context = _context_builder.build(
        conversation_id=conversation_id,
        state=state,
        user_id=user_id,
        draft_request=draft,
        canonical_response=canonical_response,
    )

    agent_result = get_agent_orchestrator().process(
        user_message=user_message,
        state=state,
        conversation_id=conversation_id,
        context=context,
        canonical_response=canonical_response,
        user_id=user_id,
    )

    meta = {
        "mode": agent_result.get("mode"),
        "tokens": agent_result.get("tokens", 0),
        "latency_ms": agent_result.get("latency_ms", 0),
        "model": agent_result.get("model"),
        "reason": agent_result.get("reason"),
        "tools": [t.get("tool") for t in agent_result.get("tool_results", [])],
    }
    _last_agent_meta[conversation_id] = meta
    content = agent_result.get("content") or canonical_response
    return content, meta


def process_message(phone: str, text: str, raw_payload: dict[str, Any] | None = None) -> str:
    """Procesa un mensaje entrante y retorna la respuesta del bot."""
    user = user_repository.get_or_create_user(phone)
    user_id = user["id"]

    conversation = conversation_repository.get_or_create_active_conversation(user_id)
    conversation_id = conversation["id"]
    state = conversation["current_state"]
    get_or_recover_session(conversation_id)

    original_text = text
    text = nlu_parser.preprocess(state, text)
    message_repository.save_inbound_message(
        conversation_id,
        user_id,
        text,
        raw_payload={
            **(raw_payload or {}),
            "original_text": original_text,
            "normalized_text": text,
        },
    )
    normalized_text = text.strip().lower()
    if state not in {HANDOFF_REQUESTED, FINISHED} and _contains_handoff_keyword(normalized_text):
        return _request_handoff(
            conversation_id,
            user_id,
            message_service.handoff_message(),
            reason="user_requested_advisor",
        )

    response = ""
    next_state = state

    if state == START:
        response = message_service.welcome_message()
        next_state = MENU

    elif state == MENU:
        is_valid, _ = validation_service.validate_menu_option(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id,
                user_id,
                message_service.invalid_menu_message() + "\n\n" + message_service.welcome_message(),
            )
            if handoff_response:
                return handoff_response
            response = message_service.invalid_menu_message() + "\n\n" + message_service.welcome_message()
            next_state = MENU
        elif text.strip() == "1":
            conversation_repository.reset_validation_failures(conversation_id)
            credit_repository.create_draft_request(user_id, conversation_id)
            response = message_service.consent_message()
            next_state = CONSENTIMIENTO
        elif text.strip() == "2":
            conversation_repository.reset_validation_failures(conversation_id)
            response = message_service.general_info_message()
            next_state = MENU
        elif text.strip() == "3":
            return _request_handoff(
                conversation_id,
                user_id,
                message_service.handoff_message(),
                reason="menu_option_3",
            )

    elif state == CONSENTIMIENTO:
        is_valid, _ = validation_service.validate_consent(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id,
                user_id,
                message_service.invalid_confirmation_message(),
            )
            if handoff_response:
                return handoff_response
            response = message_service.invalid_confirmation_message()
            next_state = CONSENTIMIENTO
        elif validation_service.is_consent_accepted(text):
            conversation_repository.reset_validation_failures(conversation_id)
            user_repository.update_user_consent(user_id)
            response = message_service.ask_cedula_message()
            next_state = ASK_CEDULA
        else:
            response = message_service.welcome_message()
            next_state = MENU

    elif state == ASK_CEDULA:
        is_valid, error_msg = validation_service.validate_cedula_input(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id,
                user_id,
                error_msg or message_service.invalid_cedula_message(),
            )
            if handoff_response:
                return handoff_response
            response = error_msg or message_service.invalid_cedula_message()
            next_state = ASK_CEDULA
        else:
            cedula = normalize_cedula(text)
            profile = credit_profile_repository.get_profile_by_cedula(cedula)
            if not profile:
                handoff_response = _handle_validation_failure(
                    conversation_id,
                    user_id,
                    message_service.cedula_not_found_message(),
                )
                if handoff_response:
                    return handoff_response
                response = message_service.cedula_not_found_message()
                next_state = ASK_CEDULA
            else:
                conversation_repository.reset_validation_failures(conversation_id)
                request = credit_repository.get_draft_request(conversation_id)
                if request:
                    credit_repository.update_profile_data(
                        request["id"],
                        cedula,
                        int(profile["credit_score"]),
                        str(profile["score_category"]),
                        str(profile["full_name"]),
                    )
                    user_repository.update_user_consent(user_id, cedula)

                eligibility = evaluate_eligibility(_profile_to_input(profile))
                if eligibility.status == "no_elegible":
                    response = message_service.not_eligible_message(eligibility.reasons)
                    next_state = NOT_ELIGIBLE
                    handoff_service.register_handoff(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        reason="not_eligible",
                        credit_request_id=request["id"] if request else None,
                    )
                else:
                    response = (
                        message_service.profile_verified_message(profile)
                        + "\n\n"
                        + message_service.ask_income_message()
                    )
                    next_state = ASK_INCOME

    elif state == NOT_ELIGIBLE:
        response = message_service.handoff_message()
        return _request_handoff(
            conversation_id,
            user_id,
            response,
            reason="not_eligible_followup",
        )

    elif state == ASK_INCOME:
        is_valid, _ = validation_service.validate_income(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, message_service.invalid_income_message()
            )
            if handoff_response:
                return handoff_response
            response = message_service.invalid_income_message()
            next_state = ASK_INCOME
        else:
            conversation_repository.reset_validation_failures(conversation_id)
            request = credit_repository.get_draft_request(conversation_id)
            if request:
                credit_repository.update_income(
                    request["id"], validation_service.parse_numeric_value(text)
                )
            response = message_service.ask_employment_message()
            next_state = ASK_EMPLOYMENT

    elif state == ASK_EMPLOYMENT:
        is_valid, error_msg = validation_service.validate_text_field(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, error_msg or "Respuesta inválida."
            )
            if handoff_response:
                return handoff_response
            response = error_msg or "Respuesta inválida."
            next_state = ASK_EMPLOYMENT
        else:
            conversation_repository.reset_validation_failures(conversation_id)
            request = credit_repository.get_draft_request(conversation_id)
            if request:
                employment = nlu_parser.parse_employment_type(text)
                credit_repository.update_employment(request["id"], employment)
            response = message_service.ask_expenses_message()
            next_state = ASK_EXPENSES

    elif state == ASK_EXPENSES:
        is_valid, error_msg = validation_service.validate_expenses(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, error_msg or "Gastos inválidos."
            )
            if handoff_response:
                return handoff_response
            response = error_msg or "Gastos inválidos."
            next_state = ASK_EXPENSES
        else:
            conversation_repository.reset_validation_failures(conversation_id)
            request = credit_repository.get_draft_request(conversation_id)
            if request:
                credit_repository.update_expenses(
                    request["id"], validation_service.parse_numeric_value(text)
                )
            response = message_service.ask_term_message()
            next_state = ASK_TERM

    elif state == ASK_TERM:
        is_valid, _ = validation_service.validate_term(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, message_service.invalid_term_message()
            )
            if handoff_response:
                return handoff_response
            response = message_service.invalid_term_message()
            next_state = ASK_TERM
        else:
            conversation_repository.reset_validation_failures(conversation_id)
            request = credit_repository.get_draft_request(conversation_id)
            if request:
                credit_repository.update_term(request["id"], int(text.strip()))
            response = message_service.ask_purpose_message()
            next_state = ASK_PURPOSE

    elif state == ASK_PURPOSE:
        is_valid, error_msg = validation_service.validate_text_field(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, error_msg or "Respuesta inválida."
            )
            if handoff_response:
                return handoff_response
            response = error_msg or "Respuesta inválida."
            next_state = ASK_PURPOSE
        else:
            conversation_repository.reset_validation_failures(conversation_id)
            request = credit_repository.get_draft_request(conversation_id)
            if not request:
                response = message_service.welcome_message()
                next_state = MENU
            else:
                credit_repository.update_purpose(request["id"], text.strip())
                request = credit_repository.get_draft_request(conversation_id)
                profile = credit_profile_repository.get_profile_by_cedula(request["cedula"])
                if not profile:
                    response = message_service.cedula_not_found_message()
                    next_state = ASK_CEDULA
                else:
                    result_data = _calculate_and_store(conversation_id, request, profile)
                    response = message_service.result_v2_message(result_data)
                    next_state = CONFIRM

    elif state == CONFIRM:
        is_valid, _ = validation_service.validate_confirmation(text)
        if not is_valid:
            handoff_response = _handle_validation_failure(
                conversation_id, user_id, message_service.invalid_confirmation_message()
            )
            if handoff_response:
                return handoff_response
            response = message_service.invalid_confirmation_message()
            next_state = CONFIRM
        elif text.strip() == "1":
            pending = _pending_evaluations.get(conversation_id)
            if pending:
                credit_repository.save_result(
                    pending["request_id"],
                    pending["monthly_payment"],
                    pending["payment_capacity"],
                    pending["result"],
                    max_amount=pending["max_amount"],
                    requested_amount=pending["suggested_amount"],
                    annual_rate=pending["annual_rate"],
                    score_category=pending["category"],
                    eligibility_status=pending["result"],
                    rejection_reasons=pending["reasons"],
                    rules_version=pending["rules_version"],
                )
                if pending["result"] == CREDIT_RESULT_OBSERVED:
                    handoff_service.register_handoff(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        reason="observed_result",
                        credit_request_id=pending["request_id"],
                    )
            _pending_evaluations.pop(conversation_id, None)
            response = message_service.registered_message()
            next_state = FINISHED
            conversation_repository.finish_conversation(conversation_id)
        elif text.strip() == "2":
            return _request_handoff(
                conversation_id,
                user_id,
                message_service.handoff_message(),
                reason="user_declined_registration",
                credit_request_id=_pending_evaluations.get(conversation_id, {}).get("request_id"),
            )

    elif state == SHOW_RESULT:
        response = message_service.finished_message()
        next_state = FINISHED
        conversation_repository.finish_conversation(conversation_id)

    elif state in {HANDOFF_REQUESTED, FINISHED}:
        user = user_repository.get_or_create_user(phone)
        conversation = conversation_repository.get_or_create_active_conversation(user["id"])
        conversation_id = conversation["id"]
        state = conversation["current_state"]
        response = message_service.welcome_message()
        next_state = MENU

    skip_agent = next_state in {HANDOFF_REQUESTED, FINISHED} or state in {HANDOFF_REQUESTED, FINISHED}
    validation_failed = next_state == state and state not in {START, SHOW_RESULT}
    skip_agent = skip_agent or validation_failed
    response = _maybe_answer_policy_question(state, text, response)
    response, agent_meta = _apply_agent_layer(
        user_message=original_text,
        state=state,
        conversation_id=conversation_id,
        user_id=user_id,
        canonical_response=response,
        skip_agent=skip_agent,
    )

    if next_state != state:
        conversation_repository.update_state(conversation_id, next_state)

    conversation_repository.update_last_message(conversation_id, response)
    sync_session_from_conversation(
        {
            "id": conversation_id,
            "current_state": next_state,
            "validation_failures": conversation.get("validation_failures", 0),
            "user_id": user_id,
        }
    )

    outbound_payload = {"agent": agent_meta, "state": next_state}
    message_repository.save_outbound_message(
        conversation_id, user_id, response, raw_payload=outbound_payload
    )
    return response
