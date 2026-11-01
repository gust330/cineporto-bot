"""Comparator and ranking engine for movies, cinemas, sessions, and prices in Porto."""
import html
from typing import List, Dict, Any, Optional
from collections import defaultdict
from cineporto.models import Movie, Session, ComparisonResult, PriceQuote


class MovieComparator:
    """Compares cinemas, sessions, dates, and prices for a movie across the Porto district."""

    def compare(self, movie: Movie, sessions: List[Session]) -> ComparisonResult:
        # Deduplicate sessions by (cinema_id, date_str, time_str, format_type)
        unique_sessions: List[Session] = []
        seen = set()
        for s in sessions:
            key = (s.cinema_id, s.date_str, s.time_str, s.format_type)
            if key not in seen:
                seen.add(key)
                unique_sessions.append(s)

        # Group by cinema
        grouped_by_cinema: Dict[str, List[Session]] = defaultdict(list)
        available_dates_set = set()
        for s in unique_sessions:
            grouped_by_cinema[s.cinema_name].append(s)
            if s.date_str:
                available_dates_set.add(s.date_str)

        # Sort sessions inside each cinema by date and time
        for cname in grouped_by_cinema:
            grouped_by_cinema[cname].sort(key=lambda x: (x.date_str, x.time_str))

        # Price comparison analysis
        cheapest_cinema = None
        cheapest_price = None

        # Look for the cheapest general standard/spectator ticket
        for s in unique_sessions:
            if not s.price_quote:
                continue
            # Compare standard 2D or best general adult price
            current_price = s.price_quote.best_general_price
            if cheapest_price is None or current_price < cheapest_price:
                cheapest_price = current_price
                cheapest_cinema = s.cinema_name

        # Detect premium format options (IMAX, 4DX, iSense, ScreenX, VIP)
        premium_options: List[Dict[str, Any]] = []
        seen_premium = set()
        for s in unique_sessions:
            if s.format_type in ["IMAX", "4DX", "iSense", "ScreenX", "VIP Luxe"]:
                pkey = (s.cinema_name, s.format_type)
                if pkey not in seen_premium:
                    seen_premium.add(pkey)
                    premium_options.append({
                        "cinema": s.cinema_name,
                        "format": s.format_type,
                        "room": s.room,
                        "price": s.price_quote.standard_price if s.price_quote else None,
                        "booking_url": s.booking_url,
                    })

        return ComparisonResult(
            movie=movie,
            grouped_by_cinema=dict(grouped_by_cinema),
            cheapest_cinema=cheapest_cinema,
            cheapest_price=cheapest_price,
            premium_options=premium_options,
            available_dates=sorted(list(available_dates_set)),
        )

    def format_telegram_message(self, result: ComparisonResult) -> str:
        """Formats the comparison into a clear, aesthetic Telegram HTML report."""
        m = result.movie
        title = html.escape(m.title_pt)
        if m.title_original and m.title_original.lower() != m.title_pt.lower():
            title += f" (<i>{html.escape(m.title_original)}</i>)"

        lines = [
            f"🎬 <b>{title}</b>",
        ]

        if m.genre or m.duration_min or m.age_rating:
            details = []
            if m.genre:
                details.append(f"🎭 {html.escape(m.genre)}")
            if m.duration_min:
                details.append(f"⏱️ {m.duration_min} min")
            if m.age_rating:
                details.append(f"🔞 {html.escape(m.age_rating)}")
            lines.append(" • ".join(details))

        if m.status == "premiere_soon" and m.release_date:
            clean_date = m.release_date.split("T")[0]
            lines.append(f"🚀 <b>Estreia prevista:</b> {clean_date}")

        lines.append("")

        if not result.grouped_by_cinema:
            if m.status == "premiere_soon":
                lines.append("ℹ️ <b>Estado:</b> Filme em pré-estreia / brevemente. As sessões e bilheteira ainda não abriram para os cinemas do distrito do Porto.")
                lines.append("Fica atento — assim que os horários forem publicados, estarão disponíveis aqui!")
            else:
                lines.append("⚠️ Nenhuma sessão encontrada neste momento para os cinemas do distrito do Porto.")
            return "\n".join(lines)

        # Comparison summary highlights
        lines.append("📊 <b>COMPARATIVO DE PREÇOS & CINEMAS (PORTO):</b>")
        if result.cheapest_cinema and result.cheapest_price is not None:
            cheapest_name = html.escape(result.cheapest_cinema)
            lines.append(f"💰 <b>Mais Económico:</b> <b>{cheapest_name}</b> (desde <b>{result.cheapest_price:.2f}€</b>)")

        # Cartão NOS highlight
        has_nos = any("NOS" in cname for cname in result.grouped_by_cinema)
        if has_nos:
            lines.append("🎟️ <b>Melhor Oferta Telecom:</b> <b>Cinemas NOS</b> com Cartão NOS / WTF (<b>2 bilhetes por 1</b> ~3.95€/cada)")

        # Premium formats highlight
        if result.premium_options:
            premium_strs = [f"<b>{html.escape(p['format'])}</b> ({html.escape(p['cinema'])})" for p in result.premium_options]
            lines.append(f"✨ <b>Salas Premium Disponíveis:</b> {', '.join(premium_strs)}")

        lines.append("")
        lines.append("📅 <b>SESSÕES POR CINEMA:</b>")

        # Detail per cinema
        for cname, s_list in result.grouped_by_cinema.items():
            first_quote = s_list[0].price_quote
            price_label = f"{first_quote.standard_price:.2f}€" if first_quote else "Consulte"
            lines.append(f"\n📍 <b>{html.escape(cname)}</b> [Base: {price_label}]")

            # Group by date inside this cinema
            by_date = defaultdict(list)
            for s in s_list:
                by_date[s.date_str].append(s)

            for d_str, day_sessions in by_date.items():
                session_badges = []
                for s in day_sessions:
                    badge = s.time_str
                    if s.format_type != "2D":
                        badge += f" <b>[{s.format_type}]</b>"
                    if s.version == "VP":
                        badge += " (VP)"
                    session_badges.append(badge)

                date_prefix = f"  🗓️ <i>{d_str}</i>:" if d_str else "  ⏰"
                lines.append(f"{date_prefix} {' | '.join(session_badges)}")

        lines.append("\n💡 <i>Dica: Envie o nome de outro filme a qualquer momento para comparar!</i>")
        return "\n".join(lines)
