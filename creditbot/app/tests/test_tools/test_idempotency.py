"""Pruebas de idempotencia en tools crediticias."""
from unittest.mock import patch

from app.tools.credit_tools import derivar_a_asesor, registrar_solicitud


@patch("app.tools.credit_tools.credit_repository.get_request_by_id")
@patch("app.tools.credit_tools.credit_repository.save_result")
def test_registrar_solicitud_idempotent_when_completed(mock_save, mock_get):
    mock_get.return_value = {"id": "r1", "status": "completed"}

    result = registrar_solicitud("r1", 100.0, 200.0, "preaprobado")

    assert result.success is True
    assert result.data["idempotent"] is True
    mock_save.assert_not_called()


@patch("app.tools.credit_tools.handoff_repository.create_handoff_case")
@patch("app.tools.credit_tools.handoff_repository.get_pending_case_for_conversation")
def test_derivar_a_asesor_idempotent_when_pending_exists(mock_pending, mock_create):
    mock_pending.return_value = {"id": "h1", "status": "pending"}

    result = derivar_a_asesor("u1", "c1", "user_requested")

    assert result.success is True
    assert result.data["idempotent"] is True
    mock_create.assert_not_called()
