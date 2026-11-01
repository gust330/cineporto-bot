# CinePorto

[![Tests](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](#development--testing)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#prerequisites)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Cinemas](https://img.shields.io/badge/cinemas-12%20covered-orange.svg)](#covered-cinemas-directory)

A fast CLI tool and Telegram bot that aggregates movie sessions, special formats, and ticket prices across all 12 cinemas in the Porto District (Portugal), comparing sessions to find the cheapest options and best discounts.

```bash
# Search and compare movie sessions across all Porto district cinemas
python3 main.py "Dune"
```

```text
A pesquisar sessões e preços no Distrito do Porto para 'Dune'...

🎬 Dune - Duna: Parte Três (Dune - Part Three)
🎭 Aventura • ⏱️ 145 min • 🔞 NA
🚀 Estreia prevista: 2026-12-15

📊 COMPARATIVO DE PREÇOS & CINEMAS (PORTO):
💰 Mais Económico: Cinemas NOS Ferrara Plaza (desde 7.90€)
🎟️ Melhor Oferta Telecom: Cinemas NOS com Cartão NOS / WTF (2 bilhetes por 1 ~3.95€/cada)
✨ Salas Premium Disponíveis: IMAX (Cinemas NOS Mar Shopping)

📅 SESSÕES POR CINEMA:

📍 Cinemas NOS NorteShopping [Base: 7.90€]
  🗓️ 2026-12-15: 00:00 | 20:40
  🗓️ 2026-12-16: 00:00 | 13:20 | 16:50 | 20:30

📍 Cinemas NOS Mar Shopping [Base: 7.90€]
  🗓️ 2026-12-15: 00:20 | 20:20 [IMAX] | 20:50 | 23:50 [IMAX]
  🗓️ 2026-12-16: 09:30 [IMAX] | 12:20 | 13:00 [IMAX] | 15:40 | 16:30 [IMAX]

📍 Cinemas NOS Parque Nascente [Base: 7.90€]
  🗓️ 2026-12-15: 00:10 | 20:40
  🗓️ 2026-12-16: 00:30 | 10:40 | 14:00 | 17:40 | 21:00
```

---

## Overview

CinePorto solves cinema fragmentation across Greater Porto. Instead of manually navigating multiple cinema chain websites with varying pricing schemes, CinePorto queries both commercial multiplexes and independent arthouse venues in parallel. It normalizes dates and screening rooms, factors in format surcharges (IMAX, 4DX, iSense, ScreenX), applies local discount schedules (e.g., Wednesday spectator days, Monday discounts, Cartão NOS 2-for-1 perks), and delivers an actionable price comparison directly in your terminal or via Telegram.

---

## Why CinePorto

Finding movie showtimes and prices across Greater Porto is notoriously fragmented:

1. **Multiplex isolation**: Cinemas NOS, UCI Cinemas, and Castello Lopes operate siloed portals with different pricing tiers, loyalty programs, and format supplements.
2. **Independent omissions**: Arthouse venues (Cinema Trindade, Passos Manuel) and municipal venues (Teatro Municipal Campo Alegre) rarely appear side-by-side with commercial multiplexes.
3. **Hidden pricing differences**: Base adult prices, spectator days, student rates, format surcharges (IMAX, 4DX, iSense, ScreenX), and 2-for-1 telecom perks (Cartão NOS / WTF) are never compared in one place.

| Feature | CinePorto | Individual Cinema Sites | Generic Aggregators |
| :--- | :---: | :---: | :---: |
| **All 12 Porto District Cinemas** | Yes | No (1 chain only) | Partial (misses pricing) |
| **Price & Discount Comparison** | Yes | No | No |
| **Special Formats (IMAX, 4DX, iSense, ScreenX)** | Yes | Filtered per cinema | Incomplete |
| **Telecom Discount Calculation (Cartão NOS/WTF)** | Yes | Cartão NOS only | No |
| **CLI & Telegram Bot Interface** | Yes | Web only | Web only |
| **No Ads or Account Required** | Yes | Ad-heavy / Cookie walls | Ad-heavy |

---

## Quickstart

### Prerequisites
- Python 3.10 or newer
- Virtual environment (`venv`)

### Installation & First Run

```bash
# 1. Clone repository
git clone https://github.com/your-username/cineporto-bot.git
cd cineporto-bot

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation by listing covered cinemas (no API keys required)
python3 main.py --cinemas
```

---

## Command Line Usage

CinePorto works directly from your shell without needing a Telegram bot token:

- **Query a Movie**: Search by Portuguese or original English title to compare sessions, rooms, formats, and prices:
  ```bash
  python3 main.py "Gladiator II"
  ```
- **Check Upcoming Premieres**: View upcoming releases in Porto with scheduled release dates:
  ```bash
  python3 main.py --estreias
  ```
- **List Covered Cinemas**: Show all 12 monitored venues categorized by municipality:
  ```bash
  python3 main.py --cinemas
  ```

---

## Telegram Bot Setup

To run CinePorto as a 24/7 interactive Telegram bot:

1. **Obtain a Bot Token**: Chat with [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`, and copy the API token.
2. **Configure Environment**: Copy `.env.example` to `.env` and fill in your token:
   ```bash
   cp .env.example .env
   ```
   ```env
   TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   HTTP_TIMEOUT_SECONDS=10
   ```
   *(CinePorto also falls back to `~/.hermes/.env` if present).*
3. **Start Polling**:
   ```bash
   python3 main.py --bot
   # or: python3 main.py
   ```

### Available Bot Commands

| Command | Description |
| :--- | :--- |
| `<Movie Name>` | Send any movie title (e.g. `Avatar`, `Gladiator`) for instant comparison |
| `/start` | Welcome guide with quick examples |
| `/cinemas` | Complete list of covered cinemas grouped by municipality |
| `/estreias` | Upcoming film premieres and expected release dates |
| `/ajuda` | Savings guide with discount days and telecom perks |

---

## Covered Cinemas Directory

CinePorto monitors 12 cinema venues across 7 municipalities in the Porto District:

| Cinema | Municipality | Chain | Premium Formats / Specialties |
| :--- | :--- | :--- | :--- |
| **Cinemas NOS NorteShopping** | Matosinhos | NOS | IMAX, ScreenX, NOS Lounge |
| **Cinemas NOS Parque Nascente** | Gondomar (Rio Tinto) | NOS | 4DX |
| **Cinemas NOS Alameda Shop & Spot** | Porto (Estádio do Dragão) | NOS | Digital 2D/3D |
| **Cinemas NOS Mar Shopping** | Matosinhos (Leça) | NOS | IMAX, Digital 2D/3D |
| **Cinemas NOS Gaia Shopping** | Vila Nova de Gaia | NOS | Digital 2D/3D |
| **Cinemas NOS Ferrara Plaza** | Paços de Ferreira | NOS | Digital 2D/3D |
| **UCI Cinemas Arrábida 20** | Vila Nova de Gaia | UCI | iSense (Dolby Atmos), VIP Luxe |
| **Castello Lopes Mira Maia Shopping** | Maia | Castello Lopes | Digital 2D/3D |
| **Cinema Trindade** | Porto (Baixa) | Independente | Arthouse / Cinema de Autor |
| **Passos Manuel** | Porto (Baixa) | Independente | Arthouse / Cultural |
| **Teatro Municipal Campo Alegre** | Porto | Municipal | Cineclube / Cultural |
| **Cinemax Penafiel** | Penafiel | Cinemax | Digital 2D/3D |

---

## Pricing & Discount Engine

CinePorto computes accurate price quotes and highlights local savings opportunities:

- **Cinemas NOS**:
  - Base Standard: **7.90€** (2D)
  - Cartão NOS / WTF: **2-for-1** perk (~**3.95€** per ticket)
  - 2ª Feira Digital: **7.35€** via app/site
  - Format supplements: IMAX (**11.50€**), 4DX (**13.50€**), ScreenX (**10.50€**), 3D (+**1.20€**)
- **UCI Cinemas Arrábida 20**:
  - Base Standard: **7.90€**
  - Dia do Espectador (Wednesdays): **5.80€**
  - Cartão UCI: **5.90€**
  - Format supplements: iSense (**10.30€**), VIP Luxe (**9.80€**)
- **Castello Lopes Mira Maia Shopping**:
  - Base Standard: **7.50€**
  - Dia do Espectador (Mondays & Wednesdays): **5.50€**
  - Student / Senior: **6.30€**
- **Cinema Trindade**:
  - Base Standard: **7.00€**
  - Mondays promotional day: **5.00€**
  - Tripass / Student Card: **5.00€**
- **Teatro Municipal Campo Alegre**:
  - Base Standard: **4.50€**
  - Municipal Student / Tripass: **3.00€**

---

## Architecture

CinePorto uses a dual-source engine to balance speed and venue coverage:

```text
                  ┌──────────────────────┐
                  │ User (CLI / Telegram)│
                  └──────────┬───────────┘
                             │ Query
                             ▼
                  ┌──────────────────────┐
                  │  CinePortoService    │
                  └──────┬────────┬──────┘
                         │        │
           ┌─────────────┘        └─────────────┐
           ▼                                    ▼
┌─────────────────────────┐          ┌─────────────────────────┐
│     NOSScraper          │          │    FilmspotScraper      │
│ (Cinemas NOS GraphQL &  │          │ (HTML Scraper for UCI,  │
│ Aggregator JSON API)    │          │ Trindade, Mira Maia)    │
└──────────┬──────────────┘          └──────────┬──────────────┘
           │                                    │
           └─────────────┐        ┌─────────────┘
                         ▼        ▼
                  ┌──────────────────────┐
                  │   MovieComparator    │
                  │ - Session dedupe     │
                  │ - Price calculation  │
                  │ - Premium formatting │
                  └──────────┬───────────┘
                             │
                             ▼
                  Formatted Comparison Output
```

- **Cinemas NOS Scraper**: Connects directly to the official Cinemas NOS GraphQL endpoints (`/graphql/execute.json/cinemas/getAllMovies`) and aggregator session endpoints for real-time ticket availability and direct purchase links.
- **Filmspot Scraper**: Parses multi-cinema session schedules for independent, municipal, and rival chains (UCI, Castello Lopes, Trindade).
- **Comparator Engine**: Normalizes screening rooms, groups sessions by cinema and date, handles version tagging (VO = Legendado, VP = Dobrado em Português), and computes the cheapest general admission price.
- **HTML Sanitization**: All movie titles, cinema names, and user queries are escaped before reaching the Telegram Bot API to prevent entity parsing errors.

---

## Development & Testing

The test suite contains 15 unit tests covering the pricing engine, scraper models, comparator logic, HTML entity security, and Telegram bot handlers:

```bash
# Run pytest with verbose output
pytest -v
```

Expected output:
```text
tests/test_bot.py::test_bot_command_start PASSED                         [  6%]
tests/test_bot.py::test_bot_command_cinemas PASSED                       [ 13%]
tests/test_bot.py::test_bot_movie_query_found PASSED                     [ 20%]
tests/test_bot.py::test_bot_movie_query_not_found PASSED                 [ 26%]
tests/test_bot.py::test_bot_query_escapes_special_characters PASSED      [ 33%]
tests/test_cinemas_data.py::test_cinema_model_and_porto_registry PASSED  [ 40%]
tests/test_cinemas_data.py::test_calculate_price_standard_and_discounts PASSED [ 46%]
tests/test_comparator.py::test_comparator_analysis PASSED                [ 53%]
tests/test_comparator.py::test_comparator_html_escaping PASSED           [ 60%]
tests/test_filmspot_scraper.py::test_filmspot_search_movies PASSED       [ 66%]
tests/test_filmspot_scraper.py::test_filmspot_get_porto_cinema_links PASSED [ 73%]
tests/test_filmspot_scraper.py::test_filmspot_parse_cinema_sessions PASSED [ 80%]
tests/test_nos_scraper.py::test_nos_search_movie PASSED                  [ 86%]
tests/test_nos_scraper.py::test_nos_get_sessions_porto_only PASSED       [ 93%]
tests/test_service.py::test_service_find_and_compare PASSED              [100%]

============================== 15 passed in 0.08s ==============================
```

---

## Project Status

- **Maturity**: Actively maintained (v1.0.0).
- **Scope**: Dedicated to the Porto District (Portugal). Venues outside the district boundaries (e.g., Lisbon, Coimbra) are filtered out automatically.
- **Dependencies**: Kept minimal (`requests`, `python-dotenv`, `pytest`) without heavyweight browser automation frameworks.

---

## Contributing & Support

- **Bug Reports & Issues**: Open an issue on GitHub describing the movie query and expected cinema sessions.
- **Pull Requests**: Pull requests are welcome. Please ensure tests pass via `pytest -v` and add test cases for any new cinema chains or format rules.
- **Reference & Documentation**: For details on the Cinemas NOS GraphQL schema or Filmspot markup structure, inspect `cineporto/nos_scraper.py` and `cineporto/filmspot_scraper.py`.

---

## License

This project is licensed under the [MIT License](LICENSE).
