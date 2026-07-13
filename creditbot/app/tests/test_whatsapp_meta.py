"""Pruebas del proveedor Meta WhatsApp."""
from app.providers.whatsapp.meta_cloud import MetaWhatsAppProvider


def test_parse_meta_inbound():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "593999999999",
                                    "id": "wamid.123",
                                    "text": {"body": "Hola"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    provider = MetaWhatsAppProvider()
    result = provider.parse_inbound(payload)
    assert result is not None
    assert result["phone"] == "593999999999"
    assert result["message"] == "Hola"
    assert result["message_id"] == "wamid.123"
