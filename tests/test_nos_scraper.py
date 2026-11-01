import pytest
from unittest.mock import patch, MagicMock
from cineporto.nos_scraper import NOSScraper

SAMPLE_MOVIES_PAYLOAD = {
    "data": {
        "movieList": {
            "items": [
                {
                    "uuid": "6db21bab-874f-4f30-b904-f9e0c7c9ff5e",
                    "title": "Clayface (ATMOS)",
                    "originaltitle": "Clayface",
                    "aggregatetitle": "Clayface",
                    "aggregateformatnumber": "32c9bbe2-e853-46e7-b47d-4701ff79192d",
                    "intheaters": True,
                    "soon": False,
                    "releasedate": "2026-10-22T01:00",
                    "duration": "108",
                    "genre": "Terror",
                    "detailurl": "/filmes/clayface--atmos--512129765.html"
                },
                {
                    "uuid": "abc-soon-123",
                    "title": "Avatar: Fire and Ash",
                    "originaltitle": "Avatar: Fire and Ash",
                    "aggregatetitle": "Avatar: Fire and Ash",
                    "aggregateformatnumber": "agg-avatar-soon",
                    "intheaters": False,
                    "soon": True,
                    "releasedate": "2026-12-18T00:00",
                    "duration": "190",
                    "genre": "Ficção Científica"
                }
            ]
        }
    }
}

SAMPLE_SESSIONS_PAYLOAD = {
    "days": [
        {
            "name": "Hoje",
            "theaters": [
                {
                    "name": "Cinemas NOS NorteShopping",
                    "theaterId": "60cd7224-4e1f-43cf-a6f7-dac90f09e8ac",
                    "sessions": [
                        {
                            "uuid": "sess-imax-1",
                            "time": "21:30",
                            "type": "IMAX",
                            "description": "Sala IMAX",
                            "operationalDate": "2026-11-01Z",
                            "format": "imax",
                            "version": "Leg"
                        },
                        {
                            "uuid": "sess-std-2",
                            "time": "18:00",
                            "type": "Normal",
                            "description": "Sala 3",
                            "operationalDate": "2026-11-01Z",
                            "format": "2d",
                            "version": "Leg"
                        }
                    ]
                },
                {
                    "name": "Cinemas NOS Parque Nascente",
                    "theaterId": "510ca29f-bfd9-4544-a5bf-db7e31508009",
                    "sessions": [
                        {
                            "uuid": "sess-4dx-1",
                            "time": "22:00",
                            "type": "4DX",
                            "description": "Sala 4DX",
                            "operationalDate": "2026-11-01Z",
                            "format": "4dx",
                            "version": "Leg"
                        }
                    ]
                },
                {
                    "name": "Cinemas NOS Colombo",  # Lisbon cinema - should be filtered out!
                    "theaterId": "lisbon-colombo",
                    "sessions": [
                        {
                            "uuid": "sess-lisbon",
                            "time": "19:00",
                            "type": "Normal",
                            "description": "Sala 1",
                            "operationalDate": "2026-11-01Z",
                            "format": "2d",
                            "version": "Leg"
                        }
                    ]
                }
            ]
        }
    ]
}


def test_nos_search_movie():
    scraper = NOSScraper()
    with patch.object(scraper, "_fetch_all_movies", return_value=SAMPLE_MOVIES_PAYLOAD["data"]["movieList"]["items"]):
        results = scraper.search_movies("Clayface")
        assert len(results) == 1
        assert results[0].title_original == "Clayface"
        assert results[0].status == "in_theaters"

        # Search upcoming premiere
        soon_results = scraper.search_movies("Avatar")
        assert len(soon_results) == 1
        assert soon_results[0].status == "premiere_soon"
        assert soon_results[0].release_date == "2026-12-18T00:00"


def test_nos_get_sessions_porto_only():
    scraper = NOSScraper()
    with patch.object(scraper, "_fetch_sessions_json", return_value=SAMPLE_SESSIONS_PAYLOAD):
        sessions = scraper.get_movie_sessions("agg-id")
        assert len(sessions) == 3  # 2 in NorteShopping + 1 in Parque Nascente; Colombo excluded!
        cinemas = {s.cinema_name for s in sessions}
        assert "Cinemas NOS Colombo" not in cinemas
        assert "Cinemas NOS NorteShopping" in cinemas
        assert "Cinemas NOS Parque Nascente" in cinemas

        # Check formats and prices
        imax_sess = next(s for s in sessions if s.format_type == "IMAX")
        assert imax_sess.time_str == "21:30"
        assert imax_sess.price_quote is not None
        assert imax_sess.price_quote.standard_price == 11.50
        assert imax_sess.booking_url is not None
        assert "sess-imax-1" in imax_sess.booking_url
