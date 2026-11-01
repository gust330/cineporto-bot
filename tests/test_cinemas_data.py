import pytest
from cineporto.models import Cinema, Session, Movie, PriceQuote, ComparisonResult
from cineporto.cinemas_data import PORTO_CINEMAS, get_cinema_by_id, calculate_price

def test_cinema_model_and_porto_registry():
    assert len(PORTO_CINEMAS) >= 8
    norte = get_cinema_by_id("nos-norteshopping")
    assert norte is not None
    assert norte.name == "Cinemas NOS NorteShopping"
    assert norte.municipality == "Matosinhos"
    assert "IMAX" in norte.special_formats

def test_calculate_price_standard_and_discounts():
    norte = get_cinema_by_id("nos-norteshopping")
    # Standard 2D
    quote_std = calculate_price(norte, format_type="2D", day_name="Sábado")
    assert quote_std.standard_price > 7.0
    assert quote_std.cartao_nos_price is not None
    assert quote_std.cartao_nos_price < 4.5  # 2 for 1 means ~half price per ticket

    # IMAX format supplement
    quote_imax = calculate_price(norte, format_type="IMAX", day_name="Sábado")
    assert quote_imax.standard_price > quote_std.standard_price

    # UCI Arrábida Wednesday discount (Dia do Espectador)
    uci = get_cinema_by_id("uci-arrabida")
    quote_uci_wed = calculate_price(uci, format_type="2D", day_name="Quarta-feira")
    quote_uci_sat = calculate_price(uci, format_type="2D", day_name="Sábado")
    assert quote_uci_wed.best_general_price < quote_uci_sat.best_general_price
    assert quote_uci_wed.best_general_price == 5.80

    # Cinema Trindade independent pricing
    trindade = get_cinema_by_id("trindade")
    quote_trindade = calculate_price(trindade, format_type="2D", day_name="Sexta-feira")
    assert quote_trindade.standard_price == 7.00
    assert quote_trindade.tripass_price == 5.00
