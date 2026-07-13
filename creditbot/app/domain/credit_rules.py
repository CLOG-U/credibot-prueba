"""Reglas de negocio crediticio v2 — decisiones deterministas."""

from dataclasses import dataclass, field

RULES_VERSION = "v2.0"

CATEGORY_EXCELLENT = "excelente"
CATEGORY_ACCEPTABLE = "aceptable"
CATEGORY_REGULAR = "regular"
CATEGORY_HIGH_RISK = "alto_riesgo"

RESULT_PREAPPROVED = "preaprobado"
RESULT_OBSERVED = "observado"
RESULT_NOT_QUALIFIED = "no_cumple"

ELIGIBLE = "elegible"
NOT_ELIGIBLE = "no_elegible"

TASA_POR_CATEGORIA = {
    CATEGORY_EXCELLENT: 0.145,
    CATEGORY_ACCEPTABLE: 0.160,
    CATEGORY_REGULAR: 0.165,
}

MONTO_MULTIPLICADOR = {
    CATEGORY_EXCELLENT: 6.0,
    CATEGORY_ACCEPTABLE: 4.0,
    CATEGORY_REGULAR: 1.5,
    CATEGORY_HIGH_RISK: 0.0,
}

INCOME_CAPACITY_RATIO = 0.35
OBSERVED_TOLERANCE = 1.15
DELINQUENCY_THRESHOLD_DAYS = 30


def categorizar_score(score: int) -> str:
    """Clasifica score 1–999 en categoría de riesgo."""
    if score >= 750:
        return CATEGORY_EXCELLENT
    if score >= 550:
        return CATEGORY_ACCEPTABLE
    if score >= 349:
        return CATEGORY_REGULAR
    return CATEGORY_HIGH_RISK


@dataclass
class CreditProfileInput:
    """Datos de perfil para evaluar elegibilidad."""

    credit_score: int
    score_category: str
    monthly_debt_payment: float = 0.0
    has_delinquency: bool = False
    delinquency_days: int = 0
    is_blacklisted: bool = False
    no_credit_history: bool = False


@dataclass
class EligibilityResult:
    """Resultado de elegibilidad antes de calcular montos."""

    status: str
    category: str
    reasons: list[str] = field(default_factory=list)
    effective_category: str = ""


@dataclass
class PrecalificationResult:
    """Resultado completo de precalificación."""

    result: str
    max_amount: float
    suggested_amount: float
    annual_rate: float
    monthly_payment: float
    payment_capacity: float
    category: str
    reasons: list[str] = field(default_factory=list)
    rules_version: str = RULES_VERSION


def evaluate_eligibility(profile: CreditProfileInput) -> EligibilityResult:
    """Determina si el perfil puede continuar con precalificación."""
    category = profile.score_category
    effective = category
    reasons: list[str] = []

    if profile.is_blacklisted:
        return EligibilityResult(
            status=NOT_ELIGIBLE,
            category=category,
            reasons=["lista_negra"],
            effective_category=category,
        )

    if profile.has_delinquency and profile.delinquency_days > DELINQUENCY_THRESHOLD_DAYS:
        return EligibilityResult(
            status=NOT_ELIGIBLE,
            category=category,
            reasons=["mora_activa"],
            effective_category=category,
        )

    if profile.credit_score < 349 or category == CATEGORY_HIGH_RISK:
        return EligibilityResult(
            status=NOT_ELIGIBLE,
            category=category,
            reasons=["score_bajo"],
            effective_category=category,
        )

    if profile.no_credit_history:
        effective = CATEGORY_REGULAR
        reasons.append("sin_historial")

    return EligibilityResult(
        status=ELIGIBLE,
        category=category,
        reasons=reasons,
        effective_category=effective,
    )


def calculate_payment_capacity(
    monthly_income: float,
    monthly_debt_payment: float,
    monthly_expenses: float,
) -> float:
    """Capacidad = 35% ingreso - cuotas actuales - gastos."""
    capacity = monthly_income * INCOME_CAPACITY_RATIO - monthly_debt_payment - monthly_expenses
    return round(max(capacity, 0.0), 2)


def calculate_french_payment(amount: float, term_months: int, annual_rate: float) -> float:
    """Cuota mensual con sistema francés."""
    if amount <= 0 or term_months <= 0:
        return 0.0
    if annual_rate <= 0:
        return round(amount / term_months, 2)

    monthly_rate = annual_rate / 12
    factor = (1 + monthly_rate) ** term_months
    payment = amount * (monthly_rate * factor) / (factor - 1)
    return round(payment, 2)


def calculate_max_amount(monthly_income: float, category: str) -> float:
    """Techo de monto según categoría e ingreso."""
    multiplier = MONTO_MULTIPLICADOR.get(category, 0.0)
    return round(monthly_income * multiplier, 2)


def _affordable_amount(
    max_amount: float,
    term_months: int,
    annual_rate: float,
    capacity: float,
) -> float:
    """Reduce monto hasta que la cuota quepa en la capacidad."""
    if max_amount <= 0 or capacity <= 0:
        return 0.0

    low, high = 0.0, max_amount
    affordable = 0.0
    while high - low > 1.0:
        mid = round((low + high) / 2, 2)
        payment = calculate_french_payment(mid, term_months, annual_rate)
        if payment <= capacity:
            affordable = mid
            low = mid
        else:
            high = mid
    return affordable


def evaluate_precalification(
    profile: CreditProfileInput,
    monthly_income: float,
    monthly_expenses: float,
    term_months: int,
    requested_amount: float | None = None,
) -> PrecalificationResult:
    """Calcula precalificación completa con reglas deterministas."""
    eligibility = evaluate_eligibility(profile)
    category = eligibility.effective_category or profile.score_category

    if eligibility.status == NOT_ELIGIBLE:
        return PrecalificationResult(
            result=RESULT_NOT_QUALIFIED,
            max_amount=0.0,
            suggested_amount=0.0,
            annual_rate=0.0,
            monthly_payment=0.0,
            payment_capacity=0.0,
            category=profile.score_category,
            reasons=eligibility.reasons,
        )

    annual_rate = TASA_POR_CATEGORIA.get(category, TASA_POR_CATEGORIA[CATEGORY_REGULAR])
    capacity = calculate_payment_capacity(
        monthly_income,
        profile.monthly_debt_payment,
        monthly_expenses,
    )
    max_amount = calculate_max_amount(monthly_income, category)
    if requested_amount is not None:
        suggested = min(requested_amount, max_amount)
    else:
        suggested = _affordable_amount(max_amount, term_months, annual_rate, capacity)
    suggested = round(max(suggested, 0.0), 2)

    monthly_payment = calculate_french_payment(suggested, term_months, annual_rate)

    reasons = list(eligibility.reasons)

    if category == CATEGORY_REGULAR:
        result = RESULT_OBSERVED
        reasons.append("categoria_regular")
    elif monthly_payment <= capacity:
        result = RESULT_PREAPPROVED
    elif monthly_payment <= capacity * OBSERVED_TOLERANCE:
        result = RESULT_OBSERVED
        reasons.append("cuota_ajustada")
    else:
        result = RESULT_NOT_QUALIFIED
        reasons.append("capacidad_insuficiente")

    return PrecalificationResult(
        result=result,
        max_amount=max_amount,
        suggested_amount=suggested,
        annual_rate=annual_rate,
        monthly_payment=monthly_payment,
        payment_capacity=capacity,
        category=category,
        reasons=reasons,
    )
