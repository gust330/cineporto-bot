"""Filmspot scraper for multi-cinema aggregation in Portugal & Porto district."""
import re
import urllib.request
import urllib.parse
import logging
from typing import List, Dict, Optional, Any
from cineporto.models import Movie, Session
from cineporto.cinemas_data import match_cinema, calculate_price, PORTO_CINEMAS

logger = logging.getLogger(__name__)


class FilmspotScraper:
    BASE_URL = "https://filmspot.pt"
    SEARCH_URL = "https://filmspot.pt/pesquisar.php"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _post_search(self, query: str) -> Optional[str]:
        data = urllib.parse.urlencode({"search_term_string": query}).encode("utf-8")
        req = urllib.request.Request(
            self.SEARCH_URL,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"Filmspot search failed: {e}")
            return None

    def _get_html(self, path: str) -> Optional[str]:
        url = self.BASE_URL + path if path.startswith("/") else path
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"Filmspot fetch failed for {url}: {e}")
            return None

    def search_movies(self, query: str) -> List[Movie]:
        html = self._post_search(query)
        if not html:
            return []

        movies: List[Movie] = []
        seen = set()

        # Match links to /filme/.../
        pattern = r'<a\s+[^>]*href=["\'](/filme/[^"\']+)["\'][^>]*>(.*?)</a>'
        for href, text in re.findall(pattern, html, re.S):
            clean_text = re.sub(r'<[^<]+?>', '', text).strip()
            if not clean_text or href in seen:
                continue
            seen.add(href)

            # Extract movie ID
            id_match = re.search(r'-(\d+)/?$', href)
            mid = id_match.group(1) if id_match else href

            # Parse titles (e.g. "Gladiador II / Gladiator II (2024)")
            title_parts = [p.strip() for p in clean_text.split("/")]
            pt_title = title_parts[0]
            orig_title = title_parts[1] if len(title_parts) > 1 else pt_title

            # Strip year from end if present
            pt_title = re.sub(r'\s*\(\d{4}\)$', '', pt_title).strip()
            orig_title = re.sub(r'\s*\(\d{4}\)$', '', orig_title).strip()

            movie = Movie(
                id=mid,
                title_pt=pt_title,
                title_original=orig_title,
                status="in_theaters",
                poster_url=None,
            )
            # Store detail path in movie ID or notes
            movie.synopsis = href  # using synopsis temporarily to store url path
            movies.append(movie)

        return movies

    def get_porto_cinema_links(self, movie_url_path: str) -> List[Dict[str, str]]:
        """
        Parses the movie page and finds all cinema links under Porto and Grande Porto headings.
        """
        html = self._get_html(movie_url_path)
        if not html:
            return []

        results: List[Dict[str, str]] = []
        seen_slugs = set()

        # Find headings and their lists
        # We care about: Porto, Grande Porto, and Norte (if in Porto district)
        sections = re.findall(r'<h4>(.*?)</h4>\s*<ul>(.*?)</ul>', html, re.S)
        for heading, ul in sections:
            h_clean = heading.strip().lower()
            is_porto_region = any(k in h_clean for k in ["porto", "grande porto"])

            links = re.findall(r'<a\s+[^>]*href=["\'](/cinema/([^/]+)/[^"\']*)["\'][^>]*>([^<]+)</a>', ul)
            for full_href, cinema_slug, cinema_name in links:
                matched = match_cinema(cinema_slug) or match_cinema(cinema_name)
                if matched and (is_porto_region or matched.id in PORTO_CINEMAS):
                    if cinema_slug not in seen_slugs:
                        seen_slugs.add(cinema_slug)
                        results.append({
                            "cinema_id": matched.id,
                            "slug": cinema_slug,
                            "name": matched.name,
                            "href": full_href,
                        })

        return results

    def parse_cinema_sessions(self, cinema_slug_or_id: str, cinema_page_href: str) -> List[Session]:
        """
        Parses the session table from a cinema movie page.
        """
        html = self._get_html(cinema_page_href)
        if not html:
            return []

        matched = match_cinema(cinema_slug_or_id)
        if not matched:
            return []

        sessions: List[Session] = []

        # Find table of sessions
        # Format:
        # <tr><th class="sala" colspan="...">Sala 1 iSense</th></tr>
        # <tr><th><span class="cinemaCartazDiaSemana">Qua</span> <span class="cinemaCartazDia">04 Nov</span></th>
        #   <td>17:30 <script type="application/ld+json">...</script></td>
        tables = re.findall(r'<table[^>]*class=["\']cinemaTabelaSessoes["\'][^>]*>(.*?)</table>', html, re.S)
        if not tables:
            # Fallback search for any table containing cinemaCartazDia
            tables = [html]

        for tbl in tables:
            current_room = "Sala"
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.S)

            for row in rows:
                # Check if row is a room header
                room_match = re.search(r'<th[^>]*class=["\']sala["\'][^>]*>(.*?)</th>', row, re.S)
                if room_match:
                    current_room = re.sub(r'<[^<]+?>', '', room_match.group(1)).strip()
                    continue

                # Check if row has date header
                date_match = re.search(r'<th[^>]*>(.*?)</th>', row, re.S)
                if not date_match:
                    continue
                date_text = re.sub(r'<[^<]+?>', ' ', date_match.group(1)).strip()
                date_clean = " ".join(date_text.split())

                # Find all <td> cells with times
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
                for cell in cells:
                    # Clean text to find time (e.g. "17:30" or "17:30 VP")
                    cell_text = re.sub(r'<script.*?</script>', '', cell, flags=re.S)
                    cell_clean = re.sub(r'<[^<]+?>', ' ', cell_text).strip()
                    time_match = re.search(r'\b(\d{1,2}:\d{2})\b', cell_clean)
                    if not time_match:
                        continue

                    s_time = time_match.group(1)
                    s_ver = "VP" if "VP" in cell_clean else "VO"

                    # Format detection from room or cell
                    fmt = "2D"
                    combined_label = (current_room + " " + cell_clean).upper()
                    if "IMAX" in combined_label:
                        fmt = "IMAX"
                    elif "ISENSE" in combined_label:
                        fmt = "iSense"
                    elif "4DX" in combined_label:
                        fmt = "4DX"
                    elif "SCREENX" in combined_label:
                        fmt = "ScreenX"
                    elif "VIP" in combined_label:
                        fmt = "VIP Luxe"
                    elif "3D" in combined_label:
                        fmt = "3D"

                    quote = calculate_price(matched, format_type=fmt, day_name=date_clean)
                    booking_url = matched.booking_url or (self.BASE_URL + cinema_page_href)

                    sess = Session(
                        cinema_id=matched.id,
                        cinema_name=matched.name,
                        room=current_room,
                        date_str=date_clean,
                        time_str=s_time,
                        format_type=fmt,
                        version=s_ver,
                        booking_url=booking_url,
                        price_quote=quote,
                    )
                    sessions.append(sess)

        return sessions
