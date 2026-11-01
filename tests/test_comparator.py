import pytest
from cineporto.models import Movie, Session, PriceQuote
from cineporto.comparator import MovieComparator

def make_session(cinema_id, cinema_name, date_str, time_str, format_type, standard_price, spectator_price=None, cartao_nos=None):
    quote = PriceQuote(
        cinema_id=cinema_id,
        cinema_name=cinema_name,
        format_type=format_type,
        standard_price=standard_price,
        spectator_day_price=spectator_price,
        cartao_nos_price=cartao_nos,
    )
    return Session(
        cinema_id=cinema_id,
        cinema_name=cinema_name,
        room="Sala 1",
        date_str=date_str,
        time_str=time_str,
        format_type=format_type,
        version="VO",
        booking_url=f"https://booking.example/{cinema_id}",
        price_quote=quote,
    )

def test_comparator_analysis():
    movie = Movie(id="test-1", title_pt="Gladiador II", title_original="Gladiator II")
    sessions = [
        # NOS NorteShopping (Standard 7.90, Cartão NOS 3.95, IMAX 11.50)
        make_session("nos-norteshopping", "Cinemas NOS NorteShopping", "Qua 04 Nov", "18:00", "2D", 7.90, cartao_nos=3.95),
        make_session("nos-norteshopping", "Cinemas NOS NorteShopping", "Qua 04 Nov", "21:30", "IMAX", 11.50, cartao_nos=5.75),
        # UCI Arrábida (Standard 7.90, Wednesday Spectator Day 5.80)
        make_session("uci-arrabida", "UCI Cinemas Arrábida 20", "Qua 04 Nov", "17:30", "2D", 7.90, spectator_price=5.80),
        # Cinema Trindade (Standard 7.00)
        make_session("trindade", "Cinema Trindade", "Qua 04 Nov", "19:00", "2D", 7.00),
    ]

    comparator = MovieComparator()
    result = comparator.compare(movie, sessions)

    assert result.movie.title_pt == "Gladiador II"
    assert len(result.grouped_by_cinema) == 3

    # Price analysis: cheapest general adult ticket on Wednesday is UCI Arrábida at 5.80€
    assert result.cheapest_cinema == "UCI Cinemas Arrábida 20"
    assert result.cheapest_price == 5.80

    # Premium options: IMAX NorteShopping
    assert len(result.premium_options) == 1
    assert result.premium_options[0]["format"] == "IMAX"
    assert result.premium_options[0]["cinema"] == "Cinemas NOS NorteShopping"

    # Telegram formatted report output
    report = comparator.format_telegram_message(result)
    assert "Gladiador II" in report
    assert "UCI Cinemas Arrábida 20" in report
    assert "5.80€" in report
    assert "IMAX" in report
    assert "Cartão NOS" in report


def test_comparator_html_escaping():
    movie = Movie(id="test-special", title_pt="Dungeons & Dragons: Honra Entre Ladrões", title_original="Dungeons & Dragons")
    sessions = [
        make_session("nos-alameda", "Cinemas NOS Alameda Shop & Spot", "Dom 01 Nov", "21:00", "2D", 7.90)
    ]
    comparator = MovieComparator()
    result = comparator.compare(movie, sessions)
    report = comparator.format_telegram_message(result)
    # & must be escaped as &amp; for Telegram HTML parser
    assert "Dungeons &amp; Dragons" in report
    assert "Cinemas NOS Alameda Shop &amp; Spot" in report
    assert "<b>Dungeons & Dragons" not in report
