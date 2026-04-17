#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os
import re
import smtplib
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from email.message import EmailMessage
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

LOG = logging.getLogger("cardmarket-monitor")
MONEY_QUANT = Decimal("0.01")


@dataclass
class Listing:
    card_name: str
    article_url: str
    quantity: int
    price: Decimal


@dataclass
class Offer:
    seller_name: str
    seller_profile_url: str
    seller_country: str
    seller_sales: int
    seller_is_professional: bool
    quantity: int
    price: Decimal


@dataclass
class Finding:
    listing: Listing
    lowest_competitor: Offer
    suggested_price: Decimal
    action: str  # "bajar" o "subir"
    reason: str


def money(value: str | float | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def parse_price(text: str) -> Decimal | None:
    clean = text.replace("€", "").replace(" ", "").strip()
    clean = clean.replace(".", "").replace(",", ".")
    try:
        return money(clean)
    except Exception:
        return None


def parse_int(text: str) -> int:
    digits = re.sub(r"\D+", "", text or "")
    return int(digits) if digits else 0


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_html(session: requests.Session, url: str, timeout: int) -> str:
    LOG.info("GET %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_our_listings(profile_html: str) -> list[Listing]:
    """
    Parser tolerante. Intenta extraer cartas desde tablas de artículos.
    Si Cardmarket cambia HTML, ajustar selectores aquí.
    """
    soup = BeautifulSoup(profile_html, "html.parser")
    listings: list[Listing] = []

    rows = soup.select("table tbody tr")
    for row in rows:
        link = row.select_one("a[href*='/Products/']")
        if not link:
            continue

        price_cell = row.find(string=re.compile(r"€"))
        qty_cell = row.find(string=re.compile(r"^\s*\d+\s*$"))
        if not price_cell:
            continue

        card_name = link.get_text(strip=True)
        article_url = link.get("href", "").strip()
        if article_url.startswith("/"):
            article_url = f"https://www.cardmarket.com{article_url}"

        price = parse_price(str(price_cell))
        if price is None:
            continue

        quantity = parse_int(str(qty_cell)) if qty_cell else 1
        listings.append(
            Listing(
                card_name=card_name,
                article_url=article_url,
                quantity=max(1, quantity),
                price=price,
            )
        )

    return dedupe_listings(listings)


def dedupe_listings(items: Iterable[Listing]) -> list[Listing]:
    seen: set[tuple[str, str, int, Decimal]] = set()
    out: list[Listing] = []
    for item in items:
        key = (item.card_name, item.article_url, item.quantity, item.price)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def parse_offers(article_html: str) -> list[Offer]:
    """
    Parser tolerante para ofertas en la página de artículo.
    Si Cardmarket cambia HTML, ajustar selectores aquí.
    """
    soup = BeautifulSoup(article_html, "html.parser")
    offers: list[Offer] = []

    rows = soup.select("table tbody tr")
    for row in rows:
        seller_link = row.select_one("a[href*='/Users/']")
        if not seller_link:
            continue

        full_row_text = row.get_text(" ", strip=True)
        price = parse_price(full_row_text)
        if price is None:
            continue

        seller_name = seller_link.get_text(strip=True)
        seller_profile_url = seller_link.get("href", "")
        if seller_profile_url.startswith("/"):
            seller_profile_url = f"https://www.cardmarket.com{seller_profile_url}"

        quantity = parse_int(full_row_text)
        sales = parse_int(full_row_text)

        country = ""
        country_el = row.select_one("span[class*='flag-icon'], span[class*='country']")
        if country_el:
            country = (country_el.get("title") or country_el.get_text(strip=True)).upper()
        if not country and "ES" in full_row_text.upper():
            country = "ES"

        is_pro = bool(re.search(r"(Powerseller|Professional|Tienda)", full_row_text, re.I))

        offers.append(
            Offer(
                seller_name=seller_name,
                seller_profile_url=seller_profile_url,
                seller_country=country,
                seller_sales=sales,
                seller_is_professional=is_pro,
                quantity=max(1, quantity),
                price=price,
            )
        )

    return offers


def normalize_country(country: str) -> str:
    c = (country or "").strip().upper()
    if c in {"ES", "SPAIN", "ESPAÑA", "ESPANA"}:
        return "ES"
    return c


def competitor_is_valid(
    offer: Offer,
    our_quantity: int,
    our_sales: int,
    non_pro_extra_sales: int,
) -> bool:
    if normalize_country(offer.seller_country) != "ES":
        return False
    if offer.quantity < our_quantity:
        return False

    if offer.seller_is_professional:
        return offer.seller_sales > our_sales
    return offer.seller_sales >= (our_sales + non_pro_extra_sales)


def analyze_listing(
    listing: Listing,
    offers: list[Offer],
    *,
    min_price: Decimal,
    our_sales: int,
    non_pro_extra_sales: int,
) -> Finding | None:
    valid = [
        o
        for o in offers
        if competitor_is_valid(o, listing.quantity, our_sales, non_pro_extra_sales)
    ]
    if not valid:
        return None

    lowest = min(valid, key=lambda o: o.price)

    if listing.price > lowest.price:
        suggested = max(min_price, money(lowest.price - Decimal("0.01")))
        if suggested >= listing.price:
            suggested = max(min_price, lowest.price)
        return Finding(
            listing=listing,
            lowest_competitor=lowest,
            suggested_price=suggested,
            action="bajar",
            reason="Hay un competidor válido más barato.",
        )

    if listing.price <= min_price and lowest.price > listing.price:
        suggested = money(max(min_price, lowest.price - Decimal("0.01")))
        if suggested > listing.price:
            return Finding(
                listing=listing,
                lowest_competitor=lowest,
                suggested_price=suggested,
                action="subir",
                reason="Estamos en precio mínimo y hay margen para subir.",
            )

    return None


def render_report(findings: list[Finding]) -> str:
    if not findings:
        return "No se detectaron cartas con precio a corregir en esta ejecución."

    lines = ["Informe de revisión de precios Cardmarket", ""]
    for i, f in enumerate(findings, start=1):
        lines.extend(
            [
                f"{i}. {f.listing.card_name}",
                f"   - URL: {f.listing.article_url}",
                f"   - Precio actual: {f.listing.price}€",
                f"   - Competidor válido más bajo: {f.lowest_competitor.price}€ ({f.lowest_competitor.seller_name})",
                f"   - Acción recomendada: {f.action} a {f.suggested_price}€",
                f"   - Motivo: {f.reason}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def send_email(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = os.environ["SMTP_TO"]
    msg.set_content(body)

    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = env_bool("SMTP_USE_TLS", True)

    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)


def load_ignored_cards(path: str) -> set[str]:
    ignored: set[str] = set()
    if not os.path.exists(path):
        return ignored

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            ignored.add(stripped)
    return ignored


def run(env_file: str, ignored_file: str) -> int:
    load_dotenv(env_file)

    username = os.getenv("CARDMARKET_USERNAME", "").strip()
    if not username:
        raise ValueError("Falta CARDMARKET_USERNAME")

    profile_urls = [u.strip() for u in os.getenv("PROFILE_URLS", "").split(",") if u.strip()]
    if not profile_urls:
        raise ValueError("Falta PROFILE_URLS")

    our_sales = int(os.getenv("OUR_TOTAL_SALES", "0"))
    min_price = money(os.getenv("MIN_PRICE_EUR", "0.02"))
    non_pro_extra_sales = int(os.getenv("NON_PRO_SELLER_EXTRA_SALES", "300"))
    timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "20"))

    ignored = load_ignored_cards(ignored_file)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
        }
    )

    findings: list[Finding] = []
    total_listings = 0

    for profile_url in profile_urls:
        profile_html = get_html(session, profile_url, timeout)
        listings = parse_our_listings(profile_html)
        LOG.info("%s: %d cartas detectadas", profile_url, len(listings))

        for listing in listings:
            total_listings += 1
            if listing.article_url in ignored:
                continue

            try:
                article_html = get_html(session, listing.article_url, timeout)
                offers = parse_offers(article_html)
                finding = analyze_listing(
                    listing,
                    offers,
                    min_price=min_price,
                    our_sales=our_sales,
                    non_pro_extra_sales=non_pro_extra_sales,
                )
                if finding:
                    findings.append(finding)
            except requests.RequestException as err:
                LOG.warning("Error consultando %s: %s", listing.article_url, err)

    report = render_report(findings)
    print(report)

    if env_bool("EMAIL_ENABLED", False):
        send_email(
            subject=f"[Cardmarket] Revisión de precios ({len(findings)} hallazgos)",
            body=report,
        )

    LOG.info("Proceso completado. Revisadas=%d, hallazgos=%d", total_listings, len(findings))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitor de precios para Cardmarket")
    parser.add_argument("--env-file", default=".env", help="Ruta al archivo .env")
    parser.add_argument(
        "--ignored-file",
        default="ignored_cards.txt",
        help="Archivo de URLs de cartas ignoradas",
    )
    parser.add_argument("--verbose", action="store_true", help="Activar logs detallados")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    try:
        return run(args.env_file, args.ignored_file)
    except Exception as err:
        LOG.exception("Fallo en ejecución: %s", err)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
