# ADR-0001: Arquitectura CrediBot v2

**Estado:** Aceptado  
**Fecha:** 2026-07-12

## Contexto

CrediBot v1 es una máquina de estados determinista con regla simple monto/plazo vs ingreso. El feedback académico exige flujo crediticio realista con cédula, perfiles ficticios, GPT + tools + RAG, auditoría y CI/CD.

## Decisión

Adoptar arquitectura híbrida:

1. **State Manager** autoriza transiciones; GPT no escribe estado directamente.
2. **domain/credit_rules.py** calcula elegibilidad, montos y cuotas (sistema francés).
3. **Tool Registry** ejecuta acciones auditables contra Supabase.
4. **RAG** con pgvector en Supabase (sin LangChain).
5. **Redis** como capa de sesión recuperable; Supabase como fuente de verdad.
6. **Meta WhatsApp Cloud API** como canal principal; Twilio como respaldo.
7. **GitHub Actions + Docker + Google Cloud Run** para CI/CD.

## Consecuencias

- Refactor de `conversation_service.py` hacia `agent/state_manager.py` + orquestador GPT.
- Migraciones SQL versionadas en `supabase/migrations/`.
- Tests v1 se mantienen como línea base y se extienden en `test_domain/`, `test_tools/`.
