# CrediBot v3.1 — Resumen de avance y pendientes

**Fecha:** 13 de julio de 2026  
**Fuente:** [plan.md](plan.md), [tareas.md](tareas.md)  
**Enfoque:** v3.1 — bloque D (Evolution) cerrado en código; pendiente E2E manual y staging

---

## Estado actual

| Métrica | Valor |
|---|---|
| Tests automatizados | **97 passing** |
| Backend producción | https://credibot-prueba.onrender.com |
| Supabase | Migraciones 001–002 + seed (003 RAG pendiente en productivo) |
| OpenAI | Activo en Render |
| Bloque D (Evolution) | **Código ✅** · E2E WhatsApp manual ⏳ |
| Rama | `main` |

---

## Completado

### Bloques A, B, C
- IA, tools, RAG (código), NLU, memoria, guardrails, idempotencia
- Ver plan.md §5–11

### Bloque D — Evolution API (sesión 12–13 jul 2026)

| Entrega | Archivo / ruta |
|---|---|
| Provider | `creditbot/app/providers/whatsapp/evolution.py` |
| Normalización webhook | `creditbot/app/schemas/evolution.py` |
| Webhook | `POST /webhook/evolution` |
| Health instancia | `GET /health/evolution` |
| Docker local | `creditbot/docker-compose.evolution.yml` |
| Guía QR / revocación | `creditbot/docs/evolution_setup.md` |
| Fixtures + tests | `creditbot/app/tests/fixtures/evolution/`, `test_whatsapp_evolution.py` (+17 tests) |

EVO-01 a EVO-14 y EVO-16: ✅ en código. EVO-15 (E2E real WhatsApp): ⏳ manual.

---

## Pendiente — próxima sesión (orden sugerido)

### P0 — Staging / cierre académico

1. **Commit del bloque D** (cambios locales sin pushear).
2. **Migración RAG:** aplicar `creditbot/supabase/migrations/003_rag_vector_search.sql` en Supabase productivo.
3. **Ingesta RAG remota:**
   ```bash
   cd creditbot
   python -c "from app.rag.ingest import ingest_all; ingest_all(persist_remote=True)"
   python scripts/evaluate_rag.py
   ```
   Documentar hit rate en `docs/rag/evaluacion.md`.
4. **Evolution E2E manual** — seguir `creditbot/docs/evolution_setup.md`:
   - Docker + instancia `credibot-pruebas` + QR
   - Webhook con túnel HTTPS
   - Recorrido completo IA + RAG + handoff
5. **15 escenarios manuales** — plan.md §13 (cédulas en plan §21).

### P1 — Opcional

- Dashboard Streamlit en Render (`creditbot-dashboard`)
- NLU baja confianza / ortografía
- TOOL-08 cobertura completa por tool
- Documentación académica y ensayo de demo

---

## Archivos del bloque D (en repo)

Ver `creditbot/docs/evolution_setup.md` y `falta.md` §Completado.

**Local (no commitear):** `creditbot/.env`, `creditbot/.env.evolution`

---

## Comandos rápidos para retomar

```bash
cd creditbot
python -m pytest app/tests -q          # debe dar 97 passed
uvicorn app.main:app --reload --port 8001

# Evolution (cuando toque E2E)
cp .env.evolution.example .env.evolution
docker compose -f docker-compose.evolution.yml up -d
```

---

## Referencias

- Plan maestro: [plan.md](plan.md)
- Tareas EPIC-13: [tareas.md](tareas.md)
- Evolution setup: [creditbot/docs/evolution_setup.md](creditbot/docs/evolution_setup.md)
