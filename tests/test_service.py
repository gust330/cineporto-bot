import pytest
from unittest.mock import patch, MagicMock
from cineporto.service import CinePortoService
from cineporto.models import Movie, Session, PriceQuote

def test_service_find_and_compare():
    service = CinePortoService()

    fake_movie_nos = Movie(
        id="nos-agg-1",
        title_pt="Gladiador II",
        title_original="Gladiator II",
        status="in_theaters"
    )

    fake_session_nos = Session(
        cinema_id="nos-norteshopping",
        cinema_name="Cinemas NOS NorteShopping",
        room="Sala IMAX",
        date_str="Qua 04 Nov",
        time_str="21:30",
        format_type="IMAX",
        price_quote=PriceQuote("nos-norteshopping", "Cinemas NOS NorteShopping", "IMAX", 11.50)
    )

    fake_session_filmspot = Session(
        cinema_id="uci-arrabida",
        cinema_name="UCI Cinemas Arrábida 20",
        room="Sala 1",
        date_str="Qua 04 Nov",
        time_str="18:00",
        format_type="2D",
        price_quote=PriceQuote("uci-arrabida", "UCI Cinemas Arrábida 20", "2D", 7.90, spectator_day_price=5.80)
    )

    with patch.object(service.nos_scraper, "search_movies", return_value=[fake_movie_nos]):
        with patch.object(service.nos_scraper, "get_movie_sessions", return_value=[fake_session_nos]):
            with patch.object(service.filmspot_scraper, "search_movies", return_value=[]):
                res = service.query_movie("Gladiator")
                assert res is not None
                assert res.movie.title_pt == "Gladiador II"
                assert "Cinemas NOS NorteShopping" in res.grouped_by_cinema
                assert len(res.grouped_by_cinema["Cinemas NOS NorteShopping"]) == 1
