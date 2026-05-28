"""Construit le site HTML statique bilingue à partir des fichiers JSON traduits."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FR_PATH = ROOT / "data" / "magnifica-fr.json"
TR_DIR = ROOT / "data" / "translated"
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

CONTENT_INDICES = list(range(8, 15))


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[àâä]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[îï]", "i", s)
    s = re.sub(r"[ôö]", "o", s)
    s = re.sub(r"[ùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60]


def linkify_refs(text: str) -> str:
    """Transforme [1], [12] etc. en liens d'ancre vers les notes."""
    return re.sub(
        r"\[(\d+)\]",
        r'<sup class="ref"><a href="#note-\1">[\1]</a></sup>',
        text,
    )


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_paragraph(p: str) -> str:
    return linkify_refs(html_escape(p))


def main():
    fr_sections = json.loads(FR_PATH.read_text(encoding="utf-8"))

    chapters = []
    for i in CONTENT_INDICES:
        fr = fr_sections[i]
        tr_path = TR_DIR / f"section_{i}.json"
        if not tr_path.exists():
            print(f"  WARN: traduction manquante section {i}, fallback identique")
            la_paragraphs = ["[Traduction en cours]"] * len(fr["paragraphs"])
        else:
            tr = json.loads(tr_path.read_text(encoding="utf-8"))
            la_paragraphs = tr["paragraphs_la"]
            if len(la_paragraphs) != len(fr["paragraphs"]):
                print(
                    f"  WARN section {i}: {len(la_paragraphs)} LA vs "
                    f"{len(fr['paragraphs'])} FR — padding"
                )
                while len(la_paragraphs) < len(fr["paragraphs"]):
                    la_paragraphs.append("")
                la_paragraphs = la_paragraphs[: len(fr["paragraphs"])]

        chapters.append(
            {
                "id": slugify(fr["title"]),
                "title_fr": fr["title"],
                "paragraphs_fr": fr["paragraphs"],
                "paragraphs_la": la_paragraphs,
            }
        )

    # Notes (section 15)
    notes = fr_sections[15]["paragraphs"] if len(fr_sections) > 15 else []

    nav_items = "\n".join(
        f'      <li><a href="#{c["id"]}">{html_escape(c["title_fr"].title())}</a></li>'
        for c in chapters
    )

    sections_html_parts = []
    for c in chapters:
        rows = []
        for fr_p, la_p in zip(c["paragraphs_fr"], c["paragraphs_la"]):
            rows.append(
                f'      <div class="row">\n'
                f'        <p class="fr">{render_paragraph(fr_p)}</p>\n'
                f'        <p class="la" lang="la">{render_paragraph(la_p)}</p>\n'
                f'      </div>'
            )
        sections_html_parts.append(
            f'    <section id="{c["id"]}" class="chapter">\n'
            f'      <h2>{html_escape(c["title_fr"].title())}</h2>\n'
            + "\n".join(rows)
            + "\n    </section>"
        )

    notes_html = ""
    if notes:
        note_items = []
        for note in notes:
            m = re.match(r"^\[(\d+)\]\s*(.*)$", note)
            if m:
                num, body = m.group(1), m.group(2)
                note_items.append(
                    f'        <li id="note-{num}"><span class="num">[{num}]</span> '
                    f"{html_escape(body)}</li>"
                )
            else:
                note_items.append(f"        <li>{html_escape(note)}</li>")
        notes_html = (
            '    <section id="notes" class="chapter notes">\n'
            "      <h2>Notes</h2>\n"
            '      <ol class="notes-list">\n'
            + "\n".join(note_items)
            + "\n      </ol>\n    </section>"
        )

    html = HTML_TEMPLATE.format(
        nav_items=nav_items,
        sections=("\n\n".join(sections_html_parts)) + ("\n\n" + notes_html if notes_html else ""),
    )

    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"-> {DOCS/'index.html'} ({len(html)} chars, {len(chapters)} chapitres)")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magnifica Humanitas — Versio Latina</title>
  <meta name="description" content="Encyclique Magnifica Humanitas de Léon XIV (2026), édition bilingue français–latin.">
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
      <p class="subtitle-fr">Sur la protection de la personne humaine à l'ère de l'intelligence artificielle</p>
      <p class="date">Romae, apud Sanctum Petrum · die XV mensis Maii anno MMXXVI</p>
    </div>
  </header>

  <nav class="toc" aria-label="Table des matières">
    <div class="container">
      <h2>Index Capitum</h2>
      <ol class="toc-list">
{nav_items}
        <li><a href="#notes">Notes</a></li>
      </ol>
    </div>
  </nav>

  <div class="controls container">
    <div class="lang-toggle" role="group" aria-label="Affichage des langues">
      <button data-mode="both" class="active">FR + LA</button>
      <button data-mode="fr">FR seul</button>
      <button data-mode="la">LA seul</button>
    </div>
  </div>

  <main class="container">
{sections}
  </main>

  <footer>
    <div class="container">
      <p>Texte original : © Libreria Editrice Vaticana — <a href="https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html" rel="noopener">vatican.va</a></p>
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
