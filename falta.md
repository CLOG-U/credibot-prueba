# CrediBot v3 — Resumen de avance y pendientes

**Fecha:** 12 de julio de 2026  
**Fuente:** [plan.md](plan.md), [tareas.md](tareas.md)  
**Enfoque:** v3 AI-first (sin cloud)

---

## 1. Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Avance v3 estimado | **~75%** |
| Tests automatizados | **61 passing** |
| GPT en flujo | Integrado (opt-in con `ENABLE_GPT_AGENT`) |
| RAG | Vectorial local + fallback keywords |
| NLU | Preprocesamiento natural por estado |
| Bloqueadores externos | Supabase real, OpenAI API key, WhatsApp staging |

---

## 2. Lo implementado en v3

### Fase 1 — GPT integrado al flujo
- `app/agent/agent_service.py` — singleton orquestador
- `app/agent/context_builder.py` — contexto seguro por estado
- `app/agent/guardrails.py` — anti-injection, anti-invención
- `app/services/conversation_service.py` — capa GPT post-determinista
- Fallback automático si GPT deshabilitado, falla o detecta injection

### Fase 2-3 — Tools y NLU
- 8 tools en registry (`registrar_mensaje` añadida)
- `app/services/nlu_parser.py` — ingreso, plazo, consentimiento, empleo natural
- Mensaje original preservado para detección de injection

### Fase 4 — RAG vectorial
- `app/rag/ingest.py` — chunking + embeddings (OpenAI o pseudo-vector)
- `app/rag/documents/faqs.md`, `privacidad.md`
- `app/rag/retriever.py` — búsqueda vectorial + keywords, rechazo sin evidencia
- `docs/rag/evaluacion.md` — dataset 20 preguntas

### Fase 5 — Memoria
- `session_store.py` — recuperación Supabase + Redis/memoria
- Sync de sesión tras cada mensaje

### Fase 6 — Guardrails y tests
- Tests: NLU, guardrails, adversarial, GPT integration, RAG vectorial
- Simulador devuelve `state`, `agent_mode`, `tokens`
- Dashboard: página **Simulador v3**

### Fase 8 — Pruebas (parcial)
- 61 tests unitarios/integración/E2E mock
- Script `scripts/test_v3_flow.py`
- Guía `docs/pruebas_v3.md`

---

## 3. Pendiente para cerrar v3

### P0 — Antes de demo académica

| Item | Estado |
|---|---|
| Aplicar migraciones + seed en Supabase real | Pendiente (código listo) |
| Pruebas manuales 15 escenarios del plan | En curso |
| `ENABLE_GPT_AGENT=true` con OpenAI real | Pendiente API key |
| RAG-07: evaluar 20 preguntas y medir hit rate | Dataset listo, falta ejecutar |
| ADM-07+: embudo y métricas tokens en dashboard | Parcial |
| SES-07 / QA-06: concurrencia y duplicados | Sin tests aún |
| WhatsApp E2E con GPT | Después del simulador |

### P1 — Post-demo

- Redis en staging
- Dashboard embudo completo
- Documentación académica sprint v3
- GOV-02/03/06 retrospectivas

### Pausado (explícito en plan v3)

- Cloud Run, GCP deploy, alarmas infra

---

## 4. Cómo comenzar pruebas ahora

```bash
cd creditbot
cp .env.example .env   # configurar SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY
uvicorn app.main:app --reload
pytest app/tests -q
python scripts/test_v3_flow.py
```

Dashboard:

```bash
streamlit run dashboard/app.py
# → Simulador v3
```

---

## 5. Commits v2 (ya en remoto)

```
ef87e9c feat(datos): migraciones v2, seed y ADR
a93d38d feat(dominio): reglas crediticias v2
1007b4d feat(agente): tools, RAG y orquestador GPT
bccebb7 feat(devops): Docker, CI y documentacion v2
60e858c test(e2e): flujo simulador v2
59003d1 docs: resumen v2 en falta.md
c18758e docs: plan v3 AI-first
```

**v3 local:** cambios sin commit aún — integración GPT, NLU, RAG vectorial, tests v3.
