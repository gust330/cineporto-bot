"""Scraper and client for Cinemas NOS GraphQL & Aggregator endpoints."""
import json
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Any
from cineporto.models import Movie, Session
from cineporto.cinemas_data import match_cinema, calculate_price, PORTO_CINEMAS

logger = logging.getLogger(__name__)


class NOSScraper:
    BASE_URL = "https://www.cinemas.nos.pt"
    GRAPHQL_ALL_MOVIES = "/graphql/execute.json/cinemas/getAllMovies"
    GRAPHQL_MOVIES_SOON = "/graphql/execute.json/cinemas/getMoviesSoon"
    GRAPHQL_THEATERS = "/graphql/execute.json/cinemas/getAllTheatersWithoutRegion"
    AGGREGATOR_SESSIONS = "/bin/cinemas/render/getMovieSessions.getMovieSessionsAggregator.json?aggregateMovieId="

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cached_movies: Optional[List[Dict[str, Any]]] = None

    def _http_get(self, path: str) -> Optional[Any]:
        url = self.BASE_URL + path if path.startswith("/") else path
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                return json.loads(text)
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return None

    def _fetch_all_movies(self) -> List[Dict[str, Any]]:
        if self._cached_movies is not None:
            return self._cached_movies
        data = self._http_get(self.GRAPHQL_ALL_MOVIES)
        items = []
        if data and isinstance(data, dict):
            items = data.get("data", {}).get("movieList", {}).get("items", [])
        self._cached_movies = items
        return items

    def _fetch_sessions_json(self, aggregate_movie_id: str) -> Optional[Dict[str, Any]]:
        path = self.AGGREGATOR_SESSIONS + urllib.parse.quote(aggregate_movie_id)
        return self._http_get(path)

    def search_movies(self, query: str) -> List[Movie]:
        items = self._fetch_all_movies()
        q = query.strip().lower()
        results: List[Movie] = []
        seen_titles = set()

        for item in items:
            title = item.get("title", "")
            orig = item.get("originaltitle", "") or title
            agg = item.get("aggregatetitle", "") or title
            combined = f"{title} {orig} {agg}".lower()

            if q in combined or combined in q or any(word in combined for word in q.split() if len(word) >= 3):
                canonical_name = (orig or title).strip()
                if canonical_name in seen_titles:
                    continue
                seen_titles.add(canonical_name)

                status = "in_theaters" if item.get("intheaters", False) else "premiere_soon"
                if item.get("soon", False):
                    status = "premiere_soon"

                dur = item.get("duration")
                duration_min = int(dur) if dur and str(dur).isdigit() else None

                movie = Movie(
                    id=item.get("aggregateformatnumber") or item.get("uuid", ""),
                    title_pt=title,
                    title_original=orig,
                    status=status,
                    release_date=item.get("releasedate"),
                    duration_min=duration_min,
                    age_rating=item.get("classification"),
                    genre=item.get("genre"),
                    synopsis=item.get("synopsis", {}).get("plaintext") if isinstance(item.get("synopsis"), dict) else item.get("synopsis"),
                    poster_url=item.get("portraitimages", {}).get("path") if isinstance(item.get("portraitimages"), dict) else None,
                )
                results.append(movie)

        return results

    def get_movie_sessions(self, aggregate_movie_id: str) -> List[Session]:
        """Fetch all sessions for this movie and keep ONLY Porto district cinemas."""
        data = self._fetch_sessions_json(aggregate_movie_id)
        if not data or not isinstance(data, dict):
            return []

        sessions: List[Session] = []
        days = data.get("days", [])

        for day_entry in days:
            day_name = day_entry.get("name", "")
            theaters = day_entry.get("theaters", [])

            for th in theaters:
                th_name = th.get("name", "")
                th_id = th.get("theaterId", "")
                matched = match_cinema(th_name)

                # Check if matched cinema is in Porto district and is NOS
                if not matched or matched.chain != "NOS":
                    continue

                for s_item in th.get("sessions", []):
                    s_uuid = s_item.get("uuid", "")
                    s_time = s_item.get("time", "")
                    s_type = (s_item.get("type") or "Normal").upper()
                    s_desc = s_item.get("description", "")
                    s_date = s_item.get("operationalDate", day_name).replace("Z", "").strip()
                    s_ver = "VP" if (s_item.get("version") or "").lower() in ["dob", "vp"] else "VO"

                    # Normalize format
                    fmt = "2D"
                    if "IMAX" in s_type or "IMAX" in s_desc.upper():
                        fmt = "IMAX"
                    elif "4DX" in s_type or "4DX" in s_desc.upper():
                        fmt = "4DX"
                    elif "SCREENX" in s_type or "SCREENX" in s_desc.upper():
                        fmt = "ScreenX"
                    elif "3D" in s_type or "3D" in (s_item.get("format") or "").upper():
                        fmt = "3D"

                    booking_url = f"https://bilheteira.cinemas.nos.pt/Cinemas/Ticket?SessionUUID={s_uuid}" if s_uuid else None
                    quote = calculate_price(matched, format_type=fmt, day_name=s_date or day_name)

                    sess = Session(
                        cinema_id=matched.id,
                        cinema_name=matched.name,
                        room=s_desc,
                        date_str=s_date,
                        time_str=s_time,
                        format_type=fmt,
                        version=s_ver,
                        booking_url=booking_url,
                        price_quote=quote,
                    )
                    sessions.append(sess)

        return sessions
