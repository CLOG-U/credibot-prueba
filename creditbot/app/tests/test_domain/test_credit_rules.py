"""Pruebas de reglas crediticias v2."""
from app.domain.credit_rules import (
    CATEGORY_ACCEPTABLE,
    CATEGORY_EXCELLENT,
    CATEGORY_HIGH_RISK,
    CATEGORY_REGULAR,
    ELIGIBLE,
    NOT_ELIGIBLE,
    CreditProfileInput,
    RESULT_NOT_QUALIFIED,
    RESULT_OBSERVED,
    RESULT_PREAPPROVED,
    calculate_french_payment,
    calculate_max_amount,
    calculate_payment_capacity,
    categorizar_score,
    evaluate_eligibility,
    evaluate_precalification,
)


def test_categorizar_score():
    assert categorizar_score(820) == CATEGORY_EXCELLENT
    assert categorizar_score(650) == CATEGORY_ACCEPTABLE
    assert categorizar_score(420) == CATEGORY_REGULAR
    assert categorizar_score(280) == CATEGORY_HIGH_RISK


def test_eligibility_high_risk():
    profile = CreditProfileInput(credit_score=280, score_category=CATEGORY_HIGH_RISK)
    result = evaluate_eligibility(profile)
    assert result.status == NOT_ELIGIBLE
    assert "score_bajo" in result.reasons


def test_eligibility_delinquency():
    profile = CreditProfileInput(
        credit_score=720,
        score_category=CATEGORY_ACCEPTABLE,
        has_delinquency=True,
        delinquency_days=45,
    )
    result = evaluate_eligibility(profile)
    assert result.status == NOT_ELIGIBLE
    assert "mora_activa" in result.reasons


def test_eligibility_no_history():
    profile = CreditProfileInput(
        credit_score=600,
        score_category=CATEGORY_ACCEPTABLE,
        no_credit_history=True,
    )
    result = evaluate_eligibility(profile)
    assert result.status == ELIGIBLE
    assert result.effective_category == CATEGORY_REGULAR


def test_payment_capacity():
    capacity = calculate_payment_capacity(1000, 100, 50)
    assert capacity == 200.0


def test_max_amount_excellent():
    assert calculate_max_amount(1000, CATEGORY_EXCELLENT) == 6000.0


def test_french_payment():
    payment = calculate_french_payment(3000, 24, 0.16)
    assert 140 < payment < 155


def test_precalification_preapproved():
    profile = CreditProfileInput(
        credit_score=820,
        score_category=CATEGORY_EXCELLENT,
        monthly_debt_payment=100,
    )
    result = evaluate_precalification(
        profile=profile,
        monthly_income=2000,
        monthly_expenses=300,
        term_months=24,
        requested_amount=4000,
    )
    assert result.result == RESULT_PREAPPROVED
    assert result.max_amount == 12000.0


def test_precalification_observed_regular():
    profile = CreditProfileInput(credit_score=420, score_category=CATEGORY_REGULAR)
    result = evaluate_precalification(
        profile=profile,
        monthly_income=1500,
        monthly_expenses=200,
        term_months=12,
        requested_amount=2000,
    )
    assert result.result == RESULT_OBSERVED


def test_precalification_not_qualified():
    profile = CreditProfileInput(credit_score=250, score_category=CATEGORY_HIGH_RISK)
    result = evaluate_precalification(
        profile=profile,
        monthly_income=1000,
        monthly_expenses=100,
        term_months=12,
    )
    assert result.result == RESULT_NOT_QUALIFIED
