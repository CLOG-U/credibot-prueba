# Variables de entorno — CrediBot v3.1

Copia `.env.example` a `.env` y completa los valores.

## Obligatorias (simulador + Supabase)

| Variable | Descripción |
|---|---|
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key |
| `APP_PUBLIC_URL` | URL pública del backend (Render o local) |

## OpenAI (opcional pero recomendado)

| Variable | Valor sugerido |
|---|---|
| `ENABLE_GPT_AGENT` | `true` |
| `LLM_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | tu API key |
| `OPENAI_MODEL` | `gpt-4o-mini` |

## Evolution API (bloque D — WhatsApp académico)

| Variable | Descripción |
|---|---|
| `WHATSAPP_PROVIDER` | `evolution` |
| `EVOLUTION_API_URL` | `http://localhost:8080` |
| `EVOLUTION_API_KEY` | API key local |
| `EVOLUTION_INSTANCE` | `credibot-pruebas` |
| `EVOLUTION_WEBHOOK_SECRET` | Secreto del webhook |

## Dashboard Streamlit

| Variable | Descripción |
|---|---|
| `ADMIN_DASHBOARD_PASSWORD` | Contraseña del panel |
| `CREDIBOT_API_URL` | URL del backend para Simulador v3 |
