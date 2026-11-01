"""Data models for CinePorto."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Cinema:
    id: str
    name: str
    chain: str  # 'NOS', 'UCI', 'Castello Lopes', 'Independente', 'Municipal'
    municipality: str  # 'Porto', 'Matosinhos', 'Vila Nova de Gaia', 'Gondomar', 'Maia', etc.
    address: str
    special_formats: List[str] = field(default_factory=list)  # ['IMAX', 'ScreenX', '4DX', 'iSense']
    filmspot_slug: Optional[str] = None
    nos_uuid: Optional[str] = None
    booking_url: Optional[str] = None


@dataclass
class PriceQuote:
    cinema_id: str
    cinema_name: str
    format_type: str
    standard_price: float
    student_price: Optional[float] = None
    senior_price: Optional[float] = None
    spectator_day_price: Optional[float] = None
    cartao_nos_price: Optional[float] = None  # Price per ticket when using 2-for-1
    tripass_price: Optional[float] = None
    notes: List[str] = field(default_factory=list)

    @property
    def best_general_price(self) -> float:
        """Lowest ticket price available to any general adult (standard or spectator day)."""
        if self.spectator_day_price is not None:
            return min(self.standard_price, self.spectator_day_price)
        return self.standard_price


@dataclass
class Session:
    cinema_id: str
    cinema_name: str
    room: str
    date_str: str  # e.g. "2026-11-01" or "Dom 01 Nov"
    time_str: str  # e.g. "18:20"
    format_type: str = "2D"  # '2D', '3D', 'IMAX', '4DX', 'ScreenX', 'iSense'
    version: str = "VO"  # 'VO' (legendado) or 'VP' (dobrado)
    booking_url: Optional[str] = None
    price_quote: Optional[PriceQuote] = None


@dataclass
class Movie:
    id: str
    title_pt: str
    title_original: Optional[str] = None
    status: str = "in_theaters"  # 'in_theaters' or 'premiere_soon'
    release_date: Optional[str] = None
    duration_min: Optional[int] = None
    age_rating: Optional[str] = None
    genre: Optional[str] = None
    synopsis: Optional[str] = None
    poster_url: Optional[str] = None
    sessions: List[Session] = field(default_factory=list)


@dataclass
class ComparisonResult:
    movie: Movie
    grouped_by_cinema: Dict[str, List[Session]] = field(default_factory=dict)
    cheapest_cinema: Optional[str] = None
    cheapest_price: Optional[float] = None
    premium_options: List[Dict[str, Any]] = field(default_factory=list)
    available_dates: List[str] = field(default_factory=list)
