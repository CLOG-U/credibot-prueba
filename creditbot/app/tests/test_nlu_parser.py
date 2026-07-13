"""Pruebas del parser NLU."""
from app.services import nlu_parser


def test_preprocess_menu_precalificar():
    assert nlu_parser.preprocess("MENU", "Quiero precalificar un crédito") == "1"


def test_preprocess_consent_si_acepto():
    assert nlu_parser.preprocess("CONSENTIMIENTO", "Sí acepto continuar") == "1"


def test_preprocess_income_natural():
    assert nlu_parser.preprocess("ASK_INCOME", "Gano unos 1200 dólares") == "1200"


def test_preprocess_expenses_natural():
    assert nlu_parser.preprocess("ASK_EXPENSES", "Gasto aproximadamente 400 al mes") == "400"


def test_preprocess_term_un_ano():
    assert nlu_parser.preprocess("ASK_TERM", "Un año") == "12"


def test_preprocess_confirm_de_acuerdo():
    assert nlu_parser.preprocess("CONFIRM", "Los datos están bien") == "1"


def test_parse_employment_independiente():
    assert nlu_parser.parse_employment_type("Soy independiente") == "independiente"
