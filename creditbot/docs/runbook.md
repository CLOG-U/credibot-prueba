# Runbook — CrediBot v2

## Despliegue

1. Aplicar migraciones en Supabase (`schema.sql`, `migrations/001`, `002`).
2. Ejecutar `seed_credit_profiles.sql`.
3. Configurar secretos en `.env` o GCP Secret Manager.
4. Desplegar imagen Docker en Cloud Run.

## Rollback

1. Revertir revisión anterior en Cloud Run.
2. No ejecutar migraciones destructivas.
3. Regenerar datos con seed si es necesario.
4. Cambiar `WHATSAPP_PROVIDER=twilio` si Meta falla.
5. Desactivar GPT con `ENABLE_GPT_AGENT=false`.

## Smoke tests

```bash
curl https://HOST/health
curl -X POST https://HOST/simulate/message -H "Content-Type: application/json" -d '{"phone":"593999999999","message":"Hola"}'
pytest app/tests -q
python scripts/test_v3_flow.py
```

Ver guía completa: `docs/pruebas_v3.md`

## Incidentes comunes

| Síntoma | Acción |
|---|---|
| Webhook duplicado | Verificar tabla `inbound_events` |
| Redis caído | El sistema usa fallback en memoria/Supabase |
| GPT timeout | Fallback determinista activo |
| Meta no responde | Usar Twilio temporalmente |
