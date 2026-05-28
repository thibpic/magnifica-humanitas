"""Construit le site bilingue dynamique :
- 7 langues vernaculaires (fr en es it de pt pl) + latin
- Données chargées en JSON côté client
- Sélecteur de langue vernaculaire à gauche, latin à droite
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
DOCS_DATA = DOCS / "data"
DOCS_DATA.mkdir(parents=True, exist_ok=True)

VERNACULAR = ["fr", "en", "es", "it", "de", "pt", "pl"]
LANG_LABELS = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "it": "Italiano",
    "de": "Deutsch",
    "pt": "Português",
    "pl": "Polski",
    "la": "Latina",
}


def slugify(s: str) -> str:
    s = s.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c"), ("ñ", "n")):
        s = re.sub(f"[{a}]", b, s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60]


def build_lang_data(lang: str) -> dict:
    """Construit chapters+notes pour une langue vernaculaire."""
    norm = json.loads((DATA / f"normalized-{lang}.json").read_text(encoding="utf-8"))
    chapters = [
        {
            "id": f"chap-{i}",
            "title": ch["title"].title() if ch["title"].isupper() else ch["title"],
            "paragraphs": ch["paragraphs"],
        }
        for i, ch in enumerate(norm["chapters"])
    ]
    return {"lang": lang, "chapters": chapters, "notes": norm["notes"]}


def build_latin_data() -> dict:
    """Construit chapters latin depuis data/translated/section_8..14.json."""
    chapters = []
    for idx, i in enumerate(range(8, 15)):
        tr = json.loads((DATA / "translated" / f"section_{i}.json").read_text(encoding="utf-8"))
        chapters.append(
            {
                "id": f"chap-{idx}",
                "title": tr["title"].title() if tr["title"].isupper() else tr["title"],
                "paragraphs": tr["paragraphs_la"],
            }
        )
    return {"lang": "la", "chapters": chapters, "notes": []}


def main():
    # Latin
    la = build_latin_data()
    (DOCS_DATA / "la.json").write_text(json.dumps(la, ensure_ascii=False), encoding="utf-8")
    print(f"la → {len(la['chapters'])} chapitres")

    # Vernaculaires
    for lang in VERNACULAR:
        d = build_lang_data(lang)
        (DOCS_DATA / f"{lang}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        n_p = sum(len(c["paragraphs"]) for c in d["chapters"])
        print(f"{lang} → {len(d['chapters'])} chapitres, {n_p} paragraphes, {len(d['notes'])} notes")

    # HTML shell
    (DOCS / "index.html").write_text(HTML, encoding="utf-8")
    print(f"-> {DOCS/'index.html'}")


HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magnifica Humanitas — Versio Latina</title>
  <meta name="description" content="Encyclique Magnifica Humanitas du pape Léon XIV (2026), édition bilingue avec traduction latine. Texte officiel en 7 langues vernaculaires.">
  <meta property="og:title" content="Magnifica Humanitas — Versio Latina">
  <meta property="og:description" content="Encyclique de Léon XIV sur l'IA, édition bilingue vernaculaire / latin.">
  <meta property="og:type" content="article">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="masthead">
    <div class="container">
      <p class="eyebrow">Litterae Encyclicae · Leo PP. XIV · MMXXVI</p>
      <h1>Magnifica Humanitas</h1>
      <p class="subtitle"><em>De persona humana tuenda aetate intellegentiae artificialis</em></p>
      <p class="subtitle-fr" id="subtitle-vern">Sur la protection de la personne humaine à l'ère de l'intelligence artificielle</p>
      <p class="date">Romae, apud Sanctum Petrum · die XV mensis Maii anno MMXXVI</p>
    </div>
  </header>

  <div class="controls container">
    <div class="lang-picker">
      <label for="vern-select">Vernacula</label>
      <select id="vern-select">
        <option value="fr">Français</option>
        <option value="en">English</option>
        <option value="es">Español</option>
        <option value="it">Italiano</option>
        <option value="de">Deutsch</option>
        <option value="pt">Português</option>
        <option value="pl">Polski</option>
      </select>
    </div>
    <div class="lang-toggle" role="group" aria-label="Affichage des langues">
      <button data-mode="both" class="active">Vern + Lat</button>
      <button data-mode="vern">Vern</button>
      <button data-mode="la">Lat</button>
    </div>
  </div>

  <nav class="toc container" aria-label="Index">
    <h2 id="toc-title">Index Capitum</h2>
    <ol class="toc-list" id="toc-list"></ol>
  </nav>

  <main class="container" id="main"></main>

  <footer>
    <div class="container">
      <p id="source-note">Texte officiel : © Libreria Editrice Vaticana — <a id="vatican-link" href="https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html" rel="noopener">vatican.va</a></p>
      <p>Traduction latine : œuvre dérivée non officielle, générée par modèle de langue (Claude Sonnet 4.6) à des fins d'étude et d'usage liturgique privé. Aucune valeur magistérielle.</p>
      <p class="small">Édition bilingue · Code source : <a href="https://github.com/thibpic/magnifica-humanitas">github.com/thibpic/magnifica-humanitas</a></p>
    </div>
  </footer>

  <script src="assets/app.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
