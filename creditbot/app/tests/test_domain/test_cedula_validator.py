"""Pruebas del validador de cédula."""
from app.domain.cedula_validator import (
    compute_check_digit,
    mask_cedula,
    normalize_cedula,
    validate_cedula,
)


def test_validate_known_valid_cedula():
    is_valid, error = validate_cedula("1713175071")
    assert is_valid is True
    assert error is None


def test_validate_invalid_check_digit():
    is_valid, error = validate_cedula("1713175070")
    assert is_valid is False
    assert error == "invalid_check_digit"


def test_validate_invalid_length():
    is_valid, error = validate_cedula("12345")
    assert is_valid is False
    assert error == "invalid_length"


def test_validate_invalid_province():
    is_valid, error = validate_cedula("2513175071")
    assert is_valid is False
    assert error == "invalid_province"


def test_compute_check_digit():
    assert compute_check_digit("171317507") == 1


def test_mask_cedula():
    assert mask_cedula("1713175071") == "17******71"


def test_normalize_cedula():
    assert normalize_cedula(" 1713-175-071 ") == "1713175071"
