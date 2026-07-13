# Meta WhatsApp Cloud API — CrediBot v2

## Configuración

Variables en `.env`:

- `META_VERIFY_TOKEN`
- `META_ACCESS_TOKEN`
- `META_PHONE_NUMBER_ID`
- `META_APP_SECRET`
- `WHATSAPP_PROVIDER=meta`

## Webhook

- **GET** `/webhook/whatsapp` — verificación Meta (`hub.mode=subscribe`)
- **POST** `/webhook/whatsapp` — mensajes JSON de Meta

## Fallback Twilio

Si Meta no está listo:

```env
WHATSAPP_PROVIDER=twilio
```

## Idempotencia

Los `message_id` se registran en `inbound_events` para evitar duplicados.
