# Evolution API — vinculación y pruebas (CrediBot v3.1)

Guía para conectar un número secundario de WhatsApp mediante Evolution API + Baileys en entorno de laboratorio.

## Requisitos

- Docker Desktop
- Número de WhatsApp secundario (no el principal)
- Túnel HTTPS (ngrok, Cloudflare Tunnel) si el backend corre en local
- Variables en `.env` del backend (ver `.env.example`)

## 1. Levantar Evolution API

```bash
cd creditbot
cp .env.evolution.example .env.evolution
# Editar AUTHENTICATION_API_KEY en .env.evolution

docker compose -f docker-compose.evolution.yml up -d
```

Comprobar: `curl http://localhost:8080` (debe responder).

## 2. Crear instancia y escanear QR

```bash
export EVO_KEY="tu-api-key-de-.env.evolution"
export INSTANCE="credibot-pruebas"

curl -X POST "http://localhost:8080/instance/create" \
  -H "apikey: $EVO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "'"$INSTANCE"'",
    "integration": "WHATSAPP-BAILEYS",
    "qrcode": true
  }'
```

Obtener QR:

```bash
curl "http://localhost:8080/instance/connect/$INSTANCE" -H "apikey: $EVO_KEY"
```

Escanear con el teléfono secundario (WhatsApp → Dispositivos vinculados → Vincular dispositivo).

Verificar conexión:

```bash
curl "http://localhost:8080/instance/connectionState/$INSTANCE" -H "apikey: $EVO_KEY"
```

Estado esperado: `open` o equivalente con sesión activa.

## 3. Configurar CrediBot

En `.env` del backend:

```env
WHATSAPP_PROVIDER=evolution
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=<misma AUTHENTICATION_API_KEY>
EVOLUTION_INSTANCE=credibot-pruebas
EVOLUTION_WEBHOOK_SECRET=<secreto-largo-aleatorio>
EVOLUTION_TIMEOUT_SECONDS=15
EVOLUTION_MAX_RETRIES=2
```

## 4. Configurar webhook entrante

URL recomendada (incluye secreto en query):

```
https://TU-TUNEL/webhook/evolution?secret=TU_EVOLUTION_WEBHOOK_SECRET
```

Alternativa: header `X-Credibot-Webhook-Secret: TU_EVOLUTION_WEBHOOK_SECRET`.

```bash
curl -X POST "http://localhost:8080/webhook/set/$INSTANCE" \
  -H "apikey: $EVO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "https://TU-TUNEL/webhook/evolution?secret=TU_SECRETO",
      "webhookByEvents": false,
      "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "CONNECTION_UPDATE"]
    }
  }'
```

## 5. Probar envío saliente

```bash
curl -X POST "http://localhost:8080/message/sendText/$INSTANCE" \
  -H "apikey: $EVO_KEY" \
  -H "Content-Type: application/json" \
  -d '{"number": "593999999999", "text": "Prueba CrediBot"}'
```

Desde CrediBot: health de instancia → `GET /health/evolution`.

## 6. Probar recepción

Enviar un mensaje de texto al número vinculado desde un teléfono autorizado.

Verificar:

1. Log del backend: inbound con teléfono enmascarado.
2. Respuesta automática del bot.
3. Registro en Supabase (`messages`, `inbound_events`).

## 7. Eventos ignorados (por diseño)

- `fromMe=true` (mensajes propios)
- Grupos (`@g.us`)
- Multimedia sin texto
- `CONNECTION_UPDATE` (solo log/debug)

## 8. Revocación del dispositivo (fin de pruebas)

1. En el teléfono: WhatsApp → Dispositivos vinculados → Cerrar sesión del dispositivo Evolution.
2. Opcional — eliminar instancia:

```bash
curl -X DELETE "http://localhost:8080/instance/delete/$INSTANCE" -H "apikey: $EVO_KEY"
```

3. Detener contenedores:

```bash
docker compose -f docker-compose.evolution.yml down
```

4. Rotar `EVOLUTION_API_KEY` y `EVOLUTION_WEBHOOK_SECRET` si se compartieron.

## Checklist de pruebas obligatorias (plan §12)

| # | Escenario | Automatizado |
|---|---|---|
| 1 | Instancia conectada/desconectada | Manual + `/health/evolution` |
| 2 | Mensaje entrante válido | Manual |
| 3 | Evento duplicado | ✅ idempotencia en `_process_inbound` |
| 4 | `fromMe=true` | ✅ `test_whatsapp_evolution.py` |
| 5 | Grupo | ✅ fixture + test |
| 6 | Sin texto | ✅ fixture + test |
| 7 | Secreto inválido | ✅ test webhook 403 |
| 8 | API key inválida al enviar | ✅ test send 401 |
| 9 | Timeout / 5xx | ✅ retry test |
| 10–15 | E2E IA, RAG, handoff, concurrencia | Manual con simulador de respaldo |

## Seguridad de laboratorio

- Solo números autorizados y con consentimiento.
- Evolution expuesto en `localhost:8080` (no abrir a Internet salvo túnel al webhook).
- No commitear `.env.evolution`, sesiones ni QR.
- Mantener el simulador activo como respaldo (`POST /simulate/message`).

## Referencias

- [Evolution API — repositorio](https://github.com/evolution-foundation/evolution-api)
- [Crear instancia](https://docs.evolutionfoundation.com.br/en/evolution-api/create-instance)
- [Configurar webhook](https://docs.evolutionfoundation.com.br/en/evolution-api/set-webhook)
- [Enviar texto](https://docs.evolutionfoundation.com.br/en/evolution-api/send-text-message)
