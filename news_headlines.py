"""
Simple script to fetch and print news headlines from Las Provincias and Levante-EMV.
"""
from __future__ import annotations

import sys
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}

# A list of selectors ordered from more specific to general so we keep titles in page order.
HEADLINE_SELECTORS: List[str] = [
    "h1 a",
    "h2 a",
    "h3 a",
    "h1",
    "h2",
    "h3",
]


def normalize_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces."""
    return " ".join(text.split())


def extract_headlines(html: str) -> list[str]:
    """Parse the provided HTML and return unique headline strings in document order."""
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    headlines: list[str] = []

    for selector in HEADLINE_SELECTORS:
        for tag in soup.select(selector):
            text = normalize_text(tag.get_text(strip=True))
            # Ignore empty strings and duplicates
            if not text or text in seen:
                continue
            seen.add(text)
            headlines.append(text)
    return headlines


def fetch_headlines(url: str, session: requests.Session) -> list[str]:
    """Download a URL and extract headline strings."""
    response = session.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return extract_headlines(response.text)


def list_all_headlines(urls: Iterable[str]) -> dict[str, list[str]]:
    """Fetch and parse headlines from each URL, returning a mapping per site."""
    session = requests.Session()
    results: dict[str, list[str]] = {}

    for url in urls:
        try:
            results[url] = fetch_headlines(url, session)
        except requests.RequestException as exc:  # pragma: no cover - defensive
            print(f"No se pudieron obtener titulares de {url}: {exc}", file=sys.stderr)
            results[url] = []
    return results


def main() -> None:
    urls = [
        "https://www.lasprovincias.es",
        "https://www.levante-emv.com",
    ]

    headlines = list_all_headlines(urls)
    for url in urls:
        print(f"\nTitulares de {url}:")
        for idx, title in enumerate(headlines.get(url, []), start=1):
            print(f"{idx:02d}. {title}")


if __name__ == "__main__":
    main()
