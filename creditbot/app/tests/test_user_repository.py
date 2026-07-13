"""Pruebas del repositorio de usuarios."""
from unittest.mock import patch

from app.repositories import user_repository


@patch("app.repositories.user_repository.get_supabase_client")
@patch("app.repositories.user_repository._cedula_belongs_to_other_user", return_value=True)
def test_update_user_consent_skips_cedula_when_used_by_other(_mock_other, mock_client):
    table = mock_client.return_value.table.return_value
    table.update.return_value.eq.return_value.execute.return_value.data = [
        {"id": "user-1", "consent_given": True}
    ]

    result = user_repository.update_user_consent("user-1", "1713175071")

    assert result["consent_given"] is True
    payload = table.update.call_args[0][0]
    assert "cedula" not in payload
