"""Master unified movie and cinema aggregator service for Porto district."""
import os
import logging
from typing import Optional, List, Dict, Any
from cineporto.models import Movie, Session, ComparisonResult
from cineporto.nos_scraper import NOSScraper
from cineporto.filmspot_scraper import FilmspotScraper
from cineporto.comparator import MovieComparator

logger = logging.getLogger(__name__)


class CinePortoService:
    def __init__(self, timeout: Optional[int] = None):
        if timeout is None:
            try:
                timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
            except (ValueError, TypeError):
                timeout = 10
        self.timeout = timeout
        self.nos_scraper = NOSScraper(timeout=timeout)
        self.filmspot_scraper = FilmspotScraper(timeout=timeout)
        self.comparator = MovieComparator()

    def query_movie(self, query: str) -> Optional[ComparisonResult]:
        """
        Search for a movie in NOS and Filmspot, aggregate all sessions across all cinemas
        in the Porto district, and run price and format comparison.
        """
        clean_q = query.strip()
        if not clean_q:
            return None

        # 1. Search NOS
        nos_movies = self.nos_scraper.search_movies(clean_q)
        # 2. Search Filmspot
        filmspot_movies = self.filmspot_scraper.search_movies(clean_q)

        chosen_movie: Optional[Movie] = None
        nos_target: Optional[Movie] = None
        filmspot_target: Optional[Movie] = None

        if nos_movies:
            nos_target = nos_movies[0]
            chosen_movie = nos_target

        if filmspot_movies:
            filmspot_target = filmspot_movies[0]
            if not chosen_movie:
                chosen_movie = filmspot_target
            else:
                # Merge metadata if needed
                if not chosen_movie.title_original and filmspot_target.title_original:
                    chosen_movie.title_original = filmspot_target.title_original

        if not chosen_movie:
            return None

        all_sessions: List[Session] = []

        # Gather sessions from NOS if matched
        if nos_target and nos_target.id:
            nos_sessions = self.nos_scraper.get_movie_sessions(nos_target.id)
            all_sessions.extend(nos_sessions)

        # Gather sessions from Filmspot for other cinemas (UCI Arrábida, Trindade, Mira Maia, etc.)
        if filmspot_target and filmspot_target.synopsis and filmspot_target.synopsis.startswith("/filme/"):
            cinema_links = self.filmspot_scraper.get_porto_cinema_links(filmspot_target.synopsis)
            for clink in cinema_links:
                # If it's a NOS cinema and we already got sessions from NOS API, skip to avoid duplicate
                if clink.get("cinema_id", "").startswith("nos-") and nos_target:
                    continue
                c_sessions = self.filmspot_scraper.parse_cinema_sessions(
                    clink["cinema_id"],
                    clink["href"]
                )
                all_sessions.extend(c_sessions)

        # Run comparison and ranking
        comparison = self.comparator.compare(chosen_movie, all_sessions)
        return comparison

    def format_comparison(self, comparison: ComparisonResult) -> str:
        return self.comparator.format_telegram_message(comparison)
