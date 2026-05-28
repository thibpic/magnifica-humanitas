"""Extrait le texte structuré de l'encyclique depuis le HTML du Vatican."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["fr", "en", "es", "it", "de", "pt", "pl"]


def extract(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")
    # Le contenu du Vatican est typiquement dans une div principale.
    # On cherche le titre puis on parcourt tous les <p> de la page de contenu.
    body = soup.find("div", class_="documento") or soup.body
    paragraphs = body.find_all(["p", "h1", "h2", "h3"])

    sections = []
    current = {"title": "Préambule", "level": 1, "paragraphs": []}

    for el in paragraphs:
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if not text:
            continue
        tag = el.name
        # Heuristique : titres en gras/centrés courts -> nouvelle section
        is_heading = tag in ("h1", "h2", "h3")
        # Détecte aussi les <p> très courts tout en majuscules / centrés
        cls = " ".join(el.get("class") or [])
        align = (el.get("style") or "") + cls
        looks_title = (
            len(text) < 120
            and (text.isupper() or "center" in align.lower() or "titolo" in cls.lower())
            and not re.match(r"^\d+\.", text)
        )
        if is_heading or looks_title:
            if current["paragraphs"]:
                sections.append(current)
            current = {"title": text, "level": 2, "paragraphs": []}
        else:
            current["paragraphs"].append(text)

    if current["paragraphs"]:
        sections.append(current)

    # Filtrer sections vides ou trop courtes (probable boilerplate de nav)
    sections = [s for s in sections if sum(len(p) for p in s["paragraphs"]) > 50]
    return sections


def main():
    for lang in LANGS:
        src = ROOT / "data" / f"magnifica-{lang}.html"
        out = ROOT / "data" / f"magnifica-{lang}.json"
        if not src.exists():
            print(f"[{lang}] source absente, skip")
            continue
        sections = extract(src)
        total_chars = sum(len(p) for s in sections for p in s["paragraphs"])
        counts = [len(s["paragraphs"]) for s in sections]
        print(f"[{lang}] {len(sections)} sections, {total_chars}c, paragraphes/sec={counts}")
        out.write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
