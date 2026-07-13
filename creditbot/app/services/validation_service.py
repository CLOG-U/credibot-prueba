"""Funciones de validación de entrada del usuario."""


def parse_numeric_value(value: str) -> float:
    """Convierte texto numérico a float, soportando coma decimal y separador de miles."""
    cleaned = value.strip().replace(" ", "")
    if "," in cleaned:
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            cleaned = parts[0].replace(".", "") + "." + parts[1]
        else:
            cleaned = cleaned.replace(",", "")
    elif "." in cleaned:
        integer_part, fractional_part = cleaned.rsplit(".", 1)
        if len(fractional_part) == 3 and integer_part.replace(".", "").isdigit():
            cleaned = cleaned.replace(".", "")
    return float(cleaned)


def validate_name(value: str) -> tuple[bool, str | None]:
    """Valida que el nombre tenga al menos 2 palabras o 5 caracteres."""
    cleaned = value.strip()
    if len(cleaned) < 5 and len(cleaned.split()) < 2:
        return False, "El nombre debe tener al menos 2 palabras o 5 caracteres."
    return True, None


def validate_amount(value: str) -> tuple[bool, str | None]:
    """Valida que el monto sea un número positivo."""
    try:
        amount = parse_numeric_value(value)
    except ValueError:
        return False, "El monto debe ser un número válido."

    if amount <= 0:
        return False, "El monto debe ser mayor a 0."

    return True, None


def validate_term(value: str) -> tuple[bool, str | None]:
    """Valida que el plazo sea un entero entre 3 y 36 meses."""
    try:
        term = int(value.strip())
    except ValueError:
        return False, "El plazo debe ser un número entero."

    if term < 3 or term > 36:
        return False, "El plazo debe estar entre 3 y 36 meses."

    return True, None


def validate_income(value: str) -> tuple[bool, str | None]:
    """Valida que el ingreso sea un número positivo."""
    try:
        income = parse_numeric_value(value)
    except ValueError:
        return False, "El ingreso debe ser un número válido."

    if income <= 0:
        return False, "El ingreso debe ser mayor a 0."

    return True, None


def validate_menu_option(value: str) -> tuple[bool, str | None]:
    """Valida que la opción del menú sea 1, 2 o 3."""
    cleaned = value.strip()
    if cleaned not in {"1", "2", "3"}:
        return False, "Selecciona una opción válida: 1, 2 o 3."
    return True, None


def validate_confirmation(value: str) -> tuple[bool, str | None]:
    """Valida que la confirmación sea 1 (Sí) o 2 (No)."""
    cleaned = value.strip()
    if cleaned not in {"1", "2"}:
        return False, "Selecciona una opción válida: 1 (Sí) o 2 (No)."
    return True, None


def validate_consent(value: str) -> tuple[bool, str | None]:
    """Valida aceptación de consentimiento."""
    cleaned = value.strip().lower()
    if cleaned in {"1", "si", "sí", "acepto", "aceptar"}:
        return True, None
    if cleaned in {"2", "no", "rechazo", "rechazar"}:
        return True, None
    return False, "Responde 1 para aceptar o 2 para rechazar."


def is_consent_accepted(value: str) -> bool:
    """Indica si el usuario aceptó el consentimiento."""
    return value.strip().lower() in {"1", "si", "sí", "acepto", "aceptar"}


def validate_cedula_input(value: str) -> tuple[bool, str | None]:
    """Valida cédula ecuatoriana con módulo 10."""
    from app.domain.cedula_validator import validate_cedula

    is_valid, error_code = validate_cedula(value)
    if not is_valid:
        messages = {
            "invalid_length": "La cédula debe tener 10 dígitos.",
            "invalid_format": "La cédula solo debe contener números.",
            "invalid_province": "Los dos primeros dígitos no corresponden a una provincia válida.",
            "invalid_person_type": "El tercer dígito no es válido para persona natural.",
            "invalid_check_digit": "El dígito verificador de la cédula no es correcto.",
        }
        return False, messages.get(error_code, "Cédula inválida.")
    return True, None


def validate_expenses(value: str) -> tuple[bool, str | None]:
    """Valida gastos mensuales (número >= 0)."""
    try:
        expenses = parse_numeric_value(value)
    except ValueError:
        return False, "Los gastos deben ser un número válido."

    if expenses < 0:
        return False, "Los gastos no pueden ser negativos."

    return True, None


def validate_text_field(value: str, min_length: int = 3) -> tuple[bool, str | None]:
    """Valida campos de texto libre con longitud mínima."""
    cleaned = value.strip()
    if len(cleaned) < min_length:
        return False, f"La respuesta debe tener al menos {min_length} caracteres."
    return True, None
