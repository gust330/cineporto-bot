import pytest
from unittest.mock import patch
from cineporto.filmspot_scraper import FilmspotScraper

SAMPLE_SEARCH_HTML = """
<html>
<body>
<div class="pure-g">
  <div class="pure-u-1 pure-u-md-3-4">
    <a href="/filme/gladiator-ii-558449/" title="Gladiador II">Gladiador II / Gladiator II (2024)</a>
    <a href="/filme/dracula-123456/" title="Dracula">Drácula / Dracula (2025)</a>
  </div>
</div>
</body>
</html>
"""

SAMPLE_MOVIE_PAGE_HTML = """
<html>
<body>
<h2>O filme "Gladiador II" está em exibição nestes cinemas</h2>
<h4>Porto</h4>
<ul>
  <li><a href="/cinema/cinema-trindade-113/558449/#558449">Cinema Trindade</a></li>
</ul>
<h4>Grande Porto</h4>
<ul>
  <li><a href="/cinema/uci-cinemas-arrabida-20-gaia-63/558449/#558449">UCI Cinemas Arrábida 20 - Gaia</a></li>
  <li><a href="/cinema/castello-lopes-mira-maia-shopping-52/558449/#558449">Castello Lopes Mira Maia Shopping</a></li>
</ul>
<h4>Lisboa</h4>
<ul>
  <li><a href="/cinema/cinema-city-campo-pequeno-lisboa-57/558449/">Cinema City Lisboa</a></li>
</ul>
</body>
</html>
"""

SAMPLE_CINEMA_SESSIONS_HTML = """
<table class="cinemaTabelaSessoes">
  <tr><th class="sala" colspan="9">Sala 1 iSense</th></tr>
  <tr>
    <th nowrap="nowrap"><span class="cinemaCartazDiaSemana">Qua</span> <span class="cinemaCartazDia">04 Nov</span></th>
    <td class="">
      17:30
      <script type="application/ld+json">{"startDate":"2026-11-04 17:30:00"}</script>
    </td>
    <td class="">
      21:00
      <script type="application/ld+json">{"startDate":"2026-11-04 21:00:00"}</script>
    </td>
  </tr>
</table>
"""


def test_filmspot_search_movies():
    scraper = FilmspotScraper()
    with patch.object(scraper, "_post_search", return_value=SAMPLE_SEARCH_HTML):
        results = scraper.search_movies("Gladiator")
        assert len(results) >= 1
        assert "Gladiador II" in results[0].title_pt
        assert "558449" in results[0].id


def test_filmspot_get_porto_cinema_links():
    scraper = FilmspotScraper()
    with patch.object(scraper, "_get_html", return_value=SAMPLE_MOVIE_PAGE_HTML):
        cinema_links = scraper.get_porto_cinema_links("/filme/gladiator-ii-558449/")
        # Should include Trindade, UCI Arrábida, Castello Lopes Mira Maia; Lisbon should be excluded!
        assert len(cinema_links) == 3
        slugs = [cl["slug"] for cl in cinema_links]
        assert "cinema-trindade-113" in slugs
        assert "uci-cinemas-arrabida-20-gaia-63" in slugs
        assert "cinema-city-campo-pequeno-lisboa-57" not in slugs


def test_filmspot_parse_cinema_sessions():
    scraper = FilmspotScraper()
    with patch.object(scraper, "_get_html", return_value=SAMPLE_CINEMA_SESSIONS_HTML):
        sessions = scraper.parse_cinema_sessions("uci-cinemas-arrabida-20-gaia-63", "/cinema/uci-cinemas-arrabida-20-gaia-63/558449/")
        assert len(sessions) == 2
        assert sessions[0].time_str == "17:30"
        assert sessions[0].date_str == "Qua 04 Nov"
        assert sessions[0].format_type == "iSense"
        assert sessions[0].cinema_name == "UCI Cinemas Arrábida 20"
        assert sessions[0].price_quote is not None
        # Wednesday is Dia do Espectador at UCI
        assert sessions[0].price_quote.spectator_day_price == 5.80
