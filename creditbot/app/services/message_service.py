"""Mensajes predefinidos del bot para cada estado de la conversación."""


def welcome_message() -> str:
    """Mensaje de bienvenida con el menú principal."""
    return (
        "Hola, soy CrediBot. Te ayudo con la *precalificación* de crédito.\n"
        "Esto no es una aprobación final ni un desembolso.\n\n"
        "¿Qué deseas hacer?\n"
        "1. Precalificar crédito\n"
        "2. Información general\n"
        "3. Hablar con asesor"
    )


def consent_message() -> str:
    """Aviso de precalificación y solicitud de consentimiento."""
    return (
        "Antes de continuar, debes saber que:\n"
        "- Esto es solo una *precalificación* con datos *ficticios* para fines académicos.\n"
        "- Usaremos tu cédula para consultar un perfil crediticio simulado.\n"
        "- Puedes pedir un asesor en cualquier momento.\n\n"
        "¿Aceptas continuar?\n"
        "1. Sí, acepto\n"
        "2. No, volver al menú"
    )


def ask_cedula_message() -> str:
    """Solicita la cédula ecuatoriana."""
    return "Ingresa tu número de cédula ecuatoriana (10 dígitos)."


def profile_verified_message(profile: dict) -> str:
    """Confirma identidad y muestra score del perfil ficticio."""
    return (
        f"Identidad verificada: {profile['full_name']}.\n"
        f"Score crediticio: {profile['credit_score']} ({profile['score_category']}).\n"
        "Continuemos con tu información financiera."
    )


def not_eligible_message(reasons: list[str]) -> str:
    """Mensaje cuando el perfil no es elegible."""
    reason_text = ", ".join(reasons) if reasons else "perfil de alto riesgo"
    return (
        f"Por el momento no cumples condiciones de precalificación ({reason_text}).\n"
        "Un asesor puede orientarte. Escribe *asesor* o selecciona la opción 3 del menú."
    )


def ask_employment_message() -> str:
    """Solicita tipo de empleo."""
    return "¿Cuál es tu situación laboral? (ej. dependiente, independiente, jubilado)"


def ask_expenses_message() -> str:
    """Solicita gastos mensuales."""
    return "¿Cuáles son tus gastos mensuales aproximados?"


def ask_purpose_message() -> str:
    """Solicita destino del crédito."""
    return "¿Para qué destinarías el crédito? (ej. educación, salud, consumo)"


def invalid_cedula_message() -> str:
    """Error de cédula inválida."""
    return "La cédula no es válida. Verifica los 10 dígitos e inténtalo de nuevo."


def cedula_not_found_message() -> str:
    """Error cuando la cédula no existe en perfiles ficticios."""
    return "No encontramos un perfil ficticio con esa cédula. Inténtalo de nuevo o pide un asesor."


def result_v2_message(data: dict) -> str:
    """Muestra resultado de precalificación v2."""
    result_labels = {
        "preaprobado": "Preaprobado",
        "observado": "Observado",
        "no_cumple": "No cumple",
    }
    label = result_labels.get(data["result"], data["result"])
    return (
        f"Resultado: {label}\n"
        f"Categoría: {data['category']}\n"
        f"Monto máximo estimado: ${data['max_amount']:.2f}\n"
        f"Monto sugerido: ${data['suggested_amount']:.2f}\n"
        f"Plazo: {data['term']} meses\n"
        f"TEA: {data['annual_rate'] * 100:.1f}%\n"
        f"Cuota estimada: ${data['monthly_payment']:.2f}\n"
        f"Capacidad de pago: ${data['payment_capacity']:.2f}\n\n"
        "¿Deseas registrar esta precalificación?\n"
        "1. Sí\n"
        "2. Hablar con asesor"
    )


def registered_message() -> str:
    """Confirmación de solicitud registrada."""
    return (
        "Solicitud registrada. Un asesor validará la documentación final.\n"
        "Gracias por usar CrediBot."
    )


def ask_term_message() -> str:
    """Solicita el plazo en meses."""
    return "¿En cuántos meses deseas pagar el crédito?"


def ask_income_message() -> str:
    """Solicita el ingreso mensual aproximado."""
    return "¿Cuál es tu ingreso mensual aproximado?"


def invalid_name_message() -> str:
    """Mensaje de error para nombre inválido."""
    return "El nombre debe tener al menos 2 palabras o 5 caracteres. Inténtalo de nuevo."


def invalid_amount_message() -> str:
    """Mensaje de error para monto inválido."""
    return "El monto debe ser un número mayor a 0. Inténtalo de nuevo."


def invalid_term_message() -> str:
    """Mensaje de error para plazo inválido."""
    return "El plazo debe ser un número entre 3 y 36 meses. Inténtalo de nuevo."


def invalid_income_message() -> str:
    """Mensaje de error para ingreso inválido."""
    return "El ingreso debe ser un número mayor a 0. Inténtalo de nuevo."


def invalid_menu_message() -> str:
    """Mensaje de error para opción de menú inválida."""
    return "Selecciona una opción válida: 1, 2 o 3."


def invalid_confirmation_message() -> str:
    """Mensaje de error para confirmación inválida."""
    return "Selecciona una opción válida: 1 (Sí) o 2 (No)."


def general_info_message() -> str:
    """Mensaje informativo con el menú principal."""
    return (
        "CrediBot te ayuda a precalificar una solicitud de crédito de forma rápida "
        "por WhatsApp. Selecciona una opción del menú:\n"
        "1. Precalificar crédito\n"
        "2. Información general\n"
        "3. Hablar con asesor"
    )


def confirm_data_message(data: dict) -> str:
    """Muestra resumen de datos para confirmación del usuario."""
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
    """Mensaje de resultado preaprobado."""
    return (
        f"Resultado: Preaprobado.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        "Un asesor puede continuar con la validación final."
    )


def observed_message(data: dict) -> str:
    """Mensaje de resultado observado (requiere revisión de asesor)."""
    return (
        f"Resultado: Observado.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        f"Capacidad de pago: ${data['payment_capacity']:.2f}\n"
        "Un asesor revisará tu caso y se comunicará contigo."
    )


def not_qualified_message(data: dict) -> str:
    """Mensaje de resultado no cumple condiciones."""
    return (
        f"Resultado: No cumple.\n"
        f"Cuota estimada: ${data['estimated_payment']:.2f}\n"
        f"Capacidad de pago: ${data['payment_capacity']:.2f}\n"
        "Por ahora no cumples las condiciones básicas de precalificación."
    )


def handoff_message() -> str:
    """Mensaje de derivación a asesor humano."""
    return (
        "Te derivaremos con un asesor humano. "
        "En breve alguien del equipo se comunicará contigo."
    )


def finished_message() -> str:
    """Mensaje de despedida al finalizar la conversación."""
    return "Gracias por usar CrediBot. Si necesitas algo más, escríbenos de nuevo."
