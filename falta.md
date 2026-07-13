# CrediBot v3.1 — Resumen de avance y pendientes

**Fecha:** 12 de julio de 2026  
**Fuente:** [plan.md](plan.md), [tareas.md](tareas.md)  
**Enfoque:** v3.1 AI + Evolution API (bloque D pendiente)

---

## Estado actual

| Métrica | Valor |
|---|---|
| Tests automatizados | **80 passing** |
| Backend producción | https://credibot-prueba.onrender.com |
| Supabase | Configurado con 25 perfiles |
| OpenAI | Activo en Render |
| Bloque D (Evolution) | **Pendiente** |

---

## Completado (bloques A, B, C, E parcial)

### A — Correcciones
- Cédula duplicada sin error 500
- Idempotencia reclamada antes de `process_message`

### B — IA y tools
- Tokens, latencia y modelo en metadata del agente
- GPT omitido en validaciones fallidas
- Tools `registrar_solicitud` y `derivar_a_asesor` idempotentes
- Tests de fallback OpenAI y tools

### C — RAG, NLU, memoria, guardrails
- RAG pgvector (`003_rag_vector_search.sql`) + retriever híbrido
- Documentos `tasas_plazos.md`, `glosario.md`
- Script `scripts/evaluate_rag.py`
- NLU gastos naturales + texto original/normalizado en mensajes
- Tests adversariales extendidos, memoria y concurrencia

### E — Configuración
- `.env.example` v3.1 con Evolution
- `docs/env_v3.1.md`, `migrations.md` actualizado
- `plan.md` línea base corregida

---

## Pendiente antes de Evolution (bloque D)

| Item | Prioridad |
|---|---|
| Aplicar migración `003_rag_vector_search.sql` en Supabase | P0 |
| Ejecutar `python scripts/evaluate_rag.py` y documentar hit rate | P0 |
| Dashboard Render (`creditbot-dashboard`) | P1 |
| 15 escenarios manuales del plan §13 | P0 |

---

## Bloque D — Evolution API (siguiente fase)

- `EvolutionWhatsAppProvider`
- Webhook `POST /webhooks/evolution`
- Docker Compose local
- E2E WhatsApp con IA

Ver plan.md §12 (EVO-01 a EVO-16).
