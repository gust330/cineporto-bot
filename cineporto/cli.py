"""CLI entrypoint for CinePorto."""
import sys
import argparse
from cineporto.service import CinePortoService
from cineporto.cinemas_data import PORTO_CINEMAS


def main():
    parser = argparse.ArgumentParser(description="CinePorto — Porto District Cinema & Movie Sessions Comparator")
    parser.add_argument("movie", nargs="?", help="Movie name to search and compare")
    parser.add_argument("--cinemas", action="store_true", help="List all covered cinemas in Porto district")
    parser.add_argument("--estreias", action="store_true", help="List upcoming movie premieres")

    args = parser.parse_args()
    service = CinePortoService()

    if args.cinemas:
        print("=== CINEMAS COBERTOS NO DISTRITO DO PORTO ===")
        for cid, c in PORTO_CINEMAS.items():
            formats = f" [{', '.join(c.special_formats)}]" if c.special_formats else ""
            print(f"- {c.name} ({c.municipality}){formats}")
        return 0

    if args.estreias:
        print("=== PRÓXIMAS ESTREIAS NOS CINEMAS DO PORTO ===")
        all_movies = service.nos_scraper.search_movies("")
        soon = [m for m in all_movies if m.status == "premiere_soon"][:10]
        for m in soon:
            date = m.release_date.split("T")[0] if m.release_date else "Brevemente"
            print(f"- {m.title_pt} ({m.title_original}) | Estreia: {date}")
        return 0

    if not args.movie:
        parser.print_help()
        return 1

    print(f"A pesquisar sessões e preços no Distrito do Porto para '{args.movie}'...")
    res = service.query_movie(args.movie)
    if not res:
        print(f"Não foram encontradas sessões nem dados para '{args.movie}'.")
        return 1

    # Remove HTML tags and unescape entities for terminal print
    import re
    import html
    raw_text = service.format_comparison(res)
    clean_text = html.unescape(re.sub(r'<[^<]+?>', '', raw_text))
    print("\n" + clean_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
