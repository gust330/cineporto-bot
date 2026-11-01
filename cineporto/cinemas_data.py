"""Porto district cinemas registry and pricing rules."""
from typing import Dict, Optional, List
from cineporto.models import Cinema, PriceQuote

# Complete directory of cinemas in the Porto District (Distrito do Porto)
PORTO_CINEMAS: Dict[str, Cinema] = {
    # 1. Cinemas NOS NorteShopping (Matosinhos)
    "nos-norteshopping": Cinema(
        id="nos-norteshopping",
        name="Cinemas NOS NorteShopping",
        chain="NOS",
        municipality="Matosinhos",
        address="Centro Comercial NorteShopping, R. Sara Afonso, Senhora da Hora, Matosinhos",
        special_formats=["IMAX", "ScreenX", "NOS Lounge"],
        filmspot_slug="cinemas-nos-norteshopping-matosinhos-35",
        nos_uuid="60cd7224-4e1f-43cf-a6f7-dac90f09e8ac",
        booking_url="https://cinemas.nos.pt",
    ),
    # 2. Cinemas NOS Parque Nascente (Rio Tinto / Gondomar)
    "nos-parquenascente": Cinema(
        id="nos-parquenascente",
        name="Cinemas NOS Parque Nascente",
        chain="NOS",
        municipality="Gondomar",
        address="Centro Comercial Parque Nascente, Praceta Parque Nascente 35, Rio Tinto",
        special_formats=["4DX"],
        filmspot_slug="cinemas-nos-parque-nascente-rio-tinto-46",
        nos_uuid="510ca29f-bfd9-4544-a5bf-db7e31508009",
        booking_url="https://cinemas.nos.pt",
    ),
    # 3. Cinemas NOS Alameda Shop & Spot (Porto)
    "nos-alameda": Cinema(
        id="nos-alameda",
        name="Cinemas NOS Alameda Shop & Spot",
        chain="NOS",
        municipality="Porto",
        address="Alameda Shop & Spot, Rua dos Campeões Europeus 28-198, Porto",
        special_formats=[],
        filmspot_slug="cinemas-nos-alameda-shop-spot-porto-41",
        nos_uuid="31a79d05-27e3-4fd4-bf19-a7259449f8da",
        booking_url="https://cinemas.nos.pt",
    ),
    # 4. Cinemas NOS Mar Shopping (Matosinhos)
    "nos-marshopping": Cinema(
        id="nos-marshopping",
        name="Cinemas NOS Mar Shopping",
        chain="NOS",
        municipality="Matosinhos",
        address="Mar Shopping Matosinhos, Av. Dr. Óscar Lopes, Leça da Palmeira",
        special_formats=[],
        filmspot_slug="cinemas-nos-mar-shopping-matosinhos-49",
        nos_uuid="feb840ea-bb8e-4203-9d71-d37690b6d5a3",
        booking_url="https://cinemas.nos.pt",
    ),
    # 5. Cinemas NOS GaiaShopping (Vila Nova de Gaia)
    "nos-gaiashopping": Cinema(
        id="nos-gaiashopping",
        name="Cinemas NOS Gaia Shopping",
        chain="NOS",
        municipality="Vila Nova de Gaia",
        address="GaiaShopping, Av. dos Descobrimentos 549, Vila Nova de Gaia",
        special_formats=[],
        filmspot_slug="cinemas-nos-gaia-shopping-31",
        nos_uuid="728fce0f-c50d-4428-9791-779d0d8d9003",
        booking_url="https://cinemas.nos.pt",
    ),
    # 6. Cinemas NOS Ferrara Plaza (Paços de Ferreira)
    "nos-ferraraplaza": Cinema(
        id="nos-ferraraplaza",
        name="Cinemas NOS Ferrara Plaza",
        chain="NOS",
        municipality="Paços de Ferreira",
        address="Ferrara Plaza, Rua das Pedreiras 36, Carvalhosa, Paços de Ferreira",
        special_formats=[],
        filmspot_slug="cinemas-nos-ferrara-plaza-pacos-de-ferreira-28",
        nos_uuid="bff605fe-f8dc-4d07-85c9-d6f3a868e65a",
        booking_url="https://cinemas.nos.pt",
    ),
    # 7. UCI Cinemas Arrábida 20 (Vila Nova de Gaia)
    "uci-arrabida": Cinema(
        id="uci-arrabida",
        name="UCI Cinemas Arrábida 20",
        chain="UCI",
        municipality="Vila Nova de Gaia",
        address="Arrábida Shopping, Praceta de Henrique Moreira 244, Vila Nova de Gaia",
        special_formats=["iSense", "VIP Luxe"],
        filmspot_slug="uci-cinemas-arrabida-20-gaia-63",
        nos_uuid=None,
        booking_url="https://www.ucicinemas.pt",
    ),
    # 8. Castello Lopes Mira Maia Shopping (Maia)
    "castello-miramaia": Cinema(
        id="castello-miramaia",
        name="Castello Lopes Mira Maia Shopping",
        chain="Castello Lopes",
        municipality="Maia",
        address="Mira Maia Shopping, Estrada Nacional 107, Moreira da Maia",
        special_formats=[],
        filmspot_slug="castello-lopes-mira-maia-shopping-52",
        nos_uuid=None,
        booking_url="https://castellolopescinemas.pt",
    ),
    # 9. Cinema Trindade (Porto downtown - Arthouse)
    "trindade": Cinema(
        id="trindade",
        name="Cinema Trindade",
        chain="Independente",
        municipality="Porto",
        address="Rua do Almada 412, Porto",
        special_formats=["Arthouse"],
        filmspot_slug="cinema-trindade-113",
        nos_uuid=None,
        booking_url="https://cinematrindade.pt",
    ),
    # 10. Cinemax Penafiel (Penafiel)
    "cinemax-penafiel": Cinema(
        id="cinemax-penafiel",
        name="Cinemax Penafiel",
        chain="Cinemax",
        municipality="Penafiel",
        address="Ponto C / Penafiel, Porto",
        special_formats=[],
        filmspot_slug="cinemax-penafiel-78",
        nos_uuid=None,
        booking_url="https://cinemax.pt",
    ),
    # 11. Teatro Municipal Campo Alegre (Porto)
    "campo-alegre": Cinema(
        id="campo-alegre",
        name="Teatro Municipal Campo Alegre",
        chain="Municipal",
        municipality="Porto",
        address="Rua das Estrelas, Porto",
        special_formats=["Cultural"],
        filmspot_slug="teatro-municipal-campo-alegre-porto-70",
        nos_uuid=None,
        booking_url="https://teatromunicipaldoporto.pt",
    ),
    # 12. Passos Manuel (Porto)
    "passos-manuel": Cinema(
        id="passos-manuel",
        name="Passos Manuel",
        chain="Independente",
        municipality="Porto",
        address="Rua de Passos Manuel 137, Porto",
        special_formats=["Arthouse"],
        filmspot_slug="passos-manuel-porto-87",
        nos_uuid=None,
        booking_url="https://passosmanuel.net",
    ),
}


def get_cinema_by_id(cinema_id: str) -> Optional[Cinema]:
    return PORTO_CINEMAS.get(cinema_id)


def match_cinema(name_or_slug: str) -> Optional[Cinema]:
    """Fuzzy match a cinema by name or slug."""
    clean = name_or_slug.lower()
    for cid, c in PORTO_CINEMAS.items():
        if cid == clean or (c.filmspot_slug and c.filmspot_slug in clean):
            return c
        if c.name.lower() in clean or clean in c.name.lower():
            return c
    # Try keywords
    if "norteshopping" in clean:
        return PORTO_CINEMAS["nos-norteshopping"]
    if "parque nascente" in clean or "rio tinto" in clean:
        return PORTO_CINEMAS["nos-parquenascente"]
    if "alameda" in clean:
        return PORTO_CINEMAS["nos-alameda"]
    if "mar shopping" in clean or "mar matosinhos" in clean:
        return PORTO_CINEMAS["nos-marshopping"]
    if "gaia shopping" in clean:
        return PORTO_CINEMAS["nos-gaiashopping"]
    if "ferrara" in clean:
        return PORTO_CINEMAS["nos-ferraraplaza"]
    if "arrabida" in clean or "arrábida" in clean or "uci" in clean:
        return PORTO_CINEMAS["uci-arrabida"]
    if "mira maia" in clean or "castello" in clean:
        return PORTO_CINEMAS["castello-miramaia"]
    if "trindade" in clean:
        return PORTO_CINEMAS["trindade"]
    if "penafiel" in clean:
        return PORTO_CINEMAS["cinemax-penafiel"]
    if "campo alegre" in clean:
        return PORTO_CINEMAS["campo-alegre"]
    if "passos manuel" in clean:
        return PORTO_CINEMAS["passos-manuel"]
    return None


def calculate_price(
    cinema: Cinema,
    format_type: str = "2D",
    day_name: Optional[str] = None
) -> PriceQuote:
    """
    Calculate full price breakdown for a given cinema, format, and day.
    """
    fmt = format_type.upper()
    day = (day_name or "").lower()
    is_wednesday = "qua" in day
    is_monday = "seg" in day

    quote = PriceQuote(
        cinema_id=cinema.id,
        cinema_name=cinema.name,
        format_type=fmt,
        standard_price=7.90,
    )

    if cinema.chain == "NOS":
        # Base pricing for Cinemas NOS
        base_std = 7.90
        # Format supplements
        if "IMAX" in fmt:
            quote.standard_price = 11.50
            quote.notes.append("Inclui taxa de ecrã IMAX")
        elif "4DX" in fmt:
            quote.standard_price = 13.50
            quote.notes.append("Inclui efeitos 4DX (movimento/água/ar)")
        elif "SCREENX" in fmt:
            quote.standard_price = 10.50
            quote.notes.append("Inclui projeção 270º ScreenX")
        elif "3D" in fmt:
            quote.standard_price = base_std + 1.20
            quote.notes.append("+1.00€ para óculos 3D se necessário")
        else:
            quote.standard_price = base_std

        if is_monday:
            quote.spectator_day_price = 7.35
            quote.notes.append("2ª feira digital: 7.35€ no site/app NOS")

        quote.student_price = 6.80
        quote.senior_price = 6.80
        # Cartão NOS / WTF perk: 2 bilhetes pelo preço de 1!
        # In 2-for-1, the price per person is half the standard price:
        quote.cartao_nos_price = round(quote.standard_price / 2.0, 2)
        quote.notes.append(f"Cartão NOS / WTF: 2 bilhetes pelo preço de 1 (~{quote.cartao_nos_price:.2f}€/cada)")

    elif cinema.chain == "UCI":
        # UCI Arrábida 20
        base_std = 7.90
        if "ISENSE" in fmt:
            quote.standard_price = 10.30
            quote.notes.append("Sala iSense com som Dolby Atmos e ecrã gigante")
        elif "VIP" in fmt:
            quote.standard_price = 9.80
            quote.notes.append("Cadeiras reclináveis VIP Luxe")
        elif "3D" in fmt:
            quote.standard_price = base_std + 1.30
        else:
            quote.standard_price = base_std

        if is_wednesday:
            quote.spectator_day_price = 5.80
            quote.notes.append("Dia do Espectador UCI (Quarta-feira): 5.80€")

        quote.student_price = 6.70
        quote.senior_price = 6.70
        quote.notes.append("Cartão UCI: 5.90€ todos os dias")

    elif cinema.chain == "Castello Lopes":
        # Mira Maia Shopping
        quote.standard_price = 7.50
        if is_wednesday or is_monday:
            quote.spectator_day_price = 5.50
            quote.notes.append("Dia do Espectador: 5.50€")
        quote.student_price = 6.30
        quote.senior_price = 6.30

    elif cinema.id == "trindade":
        # Cinema Trindade
        quote.standard_price = 7.00
        quote.student_price = 5.50
        quote.senior_price = 5.50
        quote.tripass_price = 5.00
        if is_monday:
            quote.spectator_day_price = 5.00
            quote.notes.append("Segunda-feira dia promocional: 5.00€")
        quote.notes.append("Cartão Tripass / Estudante: 5.00€")

    elif cinema.chain == "Municipal":
        # Campo Alegre / Rivoli
        quote.standard_price = 4.50
        quote.student_price = 3.00
        quote.senior_price = 3.00
        quote.tripass_price = 3.00
        quote.notes.append("Tarifa municipal reduzida para estudantes e Tripass: 3.00€")

    else:
        # Cinemax Penafiel / Outros
        quote.standard_price = 7.00
        quote.student_price = 6.00
        quote.senior_price = 6.00

    return quote
