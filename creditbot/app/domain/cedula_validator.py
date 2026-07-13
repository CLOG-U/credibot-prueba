"""Validación de cédula ecuatoriana (módulo 10)."""

PROVINCE_MIN = 1
PROVINCE_MAX = 24
COEFFICIENTS = (2, 1, 2, 1, 2, 1, 2, 1, 2)


def normalize_cedula(value: str) -> str:
    """Elimina espacios y deja solo dígitos."""
    return "".join(ch for ch in value.strip() if ch.isdigit())


def compute_check_digit(first_nine: str) -> int:
    """Calcula el dígito verificador con módulo 10."""
    total = 0
    for digit, coeff in zip(first_nine, COEFFICIENTS):
        product = int(digit) * coeff
        if product > 9:
            product -= 9
        total += product
    return (10 - (total % 10)) % 10


def validate_cedula(value: str) -> tuple[bool, str | None]:
    """
    Valida formato y dígito verificador de una cédula ecuatoriana.

    Retorna (es_válida, código_error).
    """
    cedula = normalize_cedula(value)

    if len(cedula) != 10:
        return False, "invalid_length"

    if not cedula.isdigit():
        return False, "invalid_format"

    province = int(cedula[:2])
    if province < PROVINCE_MIN or province > PROVINCE_MAX:
        return False, "invalid_province"

    third_digit = int(cedula[2])
    if third_digit >= 6:
        return False, "invalid_person_type"

    expected = compute_check_digit(cedula[:9])
    if int(cedula[9]) != expected:
        return False, "invalid_check_digit"

    return True, None


def mask_cedula(value: str) -> str:
    """Enmascara cédula para logs: 09******78."""
    cedula = normalize_cedula(value)
    if len(cedula) != 10:
        return "**********"
    return f"{cedula[:2]}******{cedula[-2:]}"
