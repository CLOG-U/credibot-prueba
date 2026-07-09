def welcome_message() -> str:
    return (
        "Hola, soy CrediBot. ¿Qué deseas hacer?\n"
        "1. Precalificar crédito\n"
        "2. Información general\n"
        "3. Hablar con asesor"
    )


def ask_name_message() -> str:
    return "Perfecto. Indícame tu nombre completo."


def ask_amount_message(name: str | None = None) -> str:
    if name:
        return f"Gracias, {name}. ¿Qué monto deseas solicitar?"
    return "¿Qué monto deseas solicitar?"


def ask_term_message() -> str:
    return "¿En cuántos meses deseas pagar el crédito?"


def ask_income_message() -> str:
    return "¿Cuál es tu ingreso mensual aproximado?"


def invalid_name_message() -> str:
    return "El nombre debe tener al menos 2 palabras o 5 caracteres. Inténtalo de nuevo."


def invalid_amount_message() -> str:
    return "El monto debe ser un número mayor a 0. Inténtalo de nuevo."


def invalid_term_message() -> str:
    return "El plazo debe ser un número entre 3 y 36 meses. Inténtalo de nuevo."


def invalid_income_message() -> str:
    return "El ingreso debe ser un número mayor a 0. Inténtalo de nuevo."


def invalid_menu_message() -> str:
    return "Selecciona una opción válida: 1, 2 o 3."


def invalid_confirmation_message() -> str:
    return "Selecciona una opción válida: 1 (Sí) o 2 (No)."


def general_info_message() -> str:
    return (
        "CrediBot te ayuda a precalificar una solicitud de crédito de forma rápida "
        "por WhatsApp. Selecciona una opción del menú:\n"
        "1. Precalificar crédito\n"
        "2. Información general\n"
        "3. Hablar con asesor"
    )


def confirm_data_message(data: dict) -> str:
    return (
        "Resumen:\n"
        f"Nombre: {data['name']}\n"
        f"Monto: ${data['amount']:.2f}\n"
        f"Plazo: {data['term']} meses\n"
        f"Ingreso: ${data['income']:.2f}\n"
        "¿Confirmas la información?\n"
        "1. Sí\n"
        "2. No"
    )


def preapproved_message(data: dict) -> str:
    return (
        f"Resultado: Preaprobado.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        "Un asesor puede continuar con la validación final."
    )


def observed_message(data: dict) -> str:
    return (
        f"Resultado: Observado.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        f"Capacidad de pago: ${data['payment_capacity']:.2f}\n"
        "Un asesor revisará tu caso y se comunicará contigo."
    )


def not_qualified_message(data: dict) -> str:
    return (
        f"Resultado: No cumple.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        f"Capacidad de pago: ${data['payment_capacity']:.2f}\n"
        "Por ahora no cumples las condiciones básicas de precalificación."
    )


def handoff_message() -> str:
    return (
        "Te derivaremos con un asesor humano. "
        "En breve alguien del equipo se comunicará contigo."
    )


def finished_message() -> str:
    return "Gracias por usar CrediBot. Si necesitas algo más, escríbenos de nuevo."
