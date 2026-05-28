"""Construit le site multilingue :
- Pages statiques pré-rendues par langue (SEO-friendly)
- Hreflang, canonical, JSON-LD sur chaque page
- sitemap.xml + robots.txt
- JS hydraté côté client pour la bascule de langue
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
DOCS_DATA = DOCS / "data"
DOCS_DATA.mkdir(parents=True, exist_ok=True)

DOMAIN = "https://magnifica-humanitas.lat"
VERNACULAR = ["fr", "en", "es", "it", "de", "pt", "pl"]
ALL_LANGS = VERNACULAR + ["la"]

LANG_LABELS = {
    "fr": "Français", "en": "English", "es": "Español", "it": "Italiano",
    "de": "Deutsch", "pt": "Português", "pl": "Polski", "la": "Latina",
}

TITLES = {
    "fr": "Magnifica Humanitas — Encyclique de Léon XIV (FR / LA)",
    "en": "Magnifica Humanitas — Encyclical of Leo XIV (EN / LA)",
    "es": "Magnifica Humanitas — Encíclica de León XIV (ES / LA)",
    "it": "Magnifica Humanitas — Enciclica di Leone XIV (IT / LA)",
    "de": "Magnifica Humanitas — Enzyklika von Leo XIV. (DE / LA)",
    "pt": "Magnifica Humanitas — Encíclica do Papa Leão XIV (PT / LA)",
    "pl": "Magnifica Humanitas — Encyklika Leona XIV (PL / LA)",
    "la": "Magnifica Humanitas — Litterae Encyclicae Leonis PP. XIV (Versio Latina)",
}

DESCRIPTIONS = {
    "fr": "Texte intégral de l'encyclique Magnifica Humanitas du pape Léon XIV (15 mai 2026) sur la protection de la personne humaine à l'ère de l'intelligence artificielle. Édition bilingue français · latin.",
    "en": "Full text of Pope Leo XIV's encyclical Magnifica Humanitas (15 May 2026) on the protection of the human person in the age of artificial intelligence. Bilingual edition English · Latin.",
    "es": "Texto íntegro de la encíclica Magnifica Humanitas del papa León XIV (15 de mayo de 2026) sobre la protección de la persona humana en la era de la inteligencia artificial. Edición bilingüe español · latín.",
    "it": "Testo integrale dell'enciclica Magnifica Humanitas di papa Leone XIV (15 maggio 2026) sulla protezione della persona umana nell'era dell'intelligenza artificiale. Edizione bilingue italiano · latino.",
    "de": "Vollständiger Text der Enzyklika Magnifica Humanitas von Papst Leo XIV. (15. Mai 2026) über den Schutz der menschlichen Person im Zeitalter der künstlichen Intelligenz. Zweisprachige Ausgabe Deutsch · Latein.",
    "pt": "Texto integral da encíclica Magnifica Humanitas do papa Leão XIV (15 de maio de 2026) sobre a proteção da pessoa humana na era da inteligência artificial. Edição bilíngue português · latim.",
    "pl": "Pełny tekst encykliki Magnifica Humanitas papieża Leona XIV (15 maja 2026) o ochronie osoby ludzkiej w erze sztucznej inteligencji. Wydanie dwujęzyczne polski · łacina.",
    "la": "Plenum textum Litterarum Encyclicarum Magnifica Humanitas Leonis PP. XIV (die XV mensis Maii anno MMXXVI) de persona humana tuenda aetate intellegentiae artificialis. Versio Latina integra.",
}

SUBTITLES = {
    "fr": "Sur la protection de la personne humaine à l'ère de l'intelligence artificielle",
    "en": "On the protection of the human person in the age of artificial intelligence",
    "es": "Sobre la protección de la persona humana en la era de la inteligencia artificial",
    "it": "Sulla protezione della persona umana nell'era dell'intelligenza artificiale",
    "de": "Über den Schutz der menschlichen Person im Zeitalter der künstlichen Intelligenz",
    "pt": "Sobre a proteção da pessoa humana na era da inteligência artificial",
    "pl": "O ochronie osoby ludzkiej w erze sztucznej inteligencji",
    "la": "De persona humana tuenda aetate intellegentiae artificialis",
}

TOC_TITLE = {
    "fr": "Sommaire", "en": "Contents", "es": "Índice", "it": "Indice",
    "de": "Inhalt", "pt": "Índice", "pl": "Spis treści", "la": "Index Capitum",
}
NOTES_LABEL = {
    "fr": "Notes", "en": "Notes", "es": "Notas", "it": "Note",
    "de": "Anmerkungen", "pt": "Notas", "pl": "Przypisy", "la": "Notae",
}
PICKER_LABEL = {
    "fr": "Langue", "en": "Language", "es": "Idioma", "it": "Lingua",
    "de": "Sprache", "pt": "Idioma", "pl": "Język", "la": "Vernacula",
}
MODE_LABELS = {
    "fr": ("Bilingue", "Vernaculaire", "Latin"),
    "en": ("Bilingual", "Vernacular", "Latin"),
    "es": ("Bilingüe", "Vernáculo", "Latín"),
    "it": ("Bilingue", "Vernacolo", "Latino"),
    "de": ("Zweisprachig", "Volkssprache", "Latein"),
    "pt": ("Bilíngue", "Vernáculo", "Latim"),
    "pl": ("Dwujęzyczny", "Wernakularny", "Łacina"),
    "la": ("Bilinguis", "Vernacula", "Latine"),
}


def linkify_refs(text: str) -> str:
    return re.sub(r"\[(\d+)\]", r'<sup class="ref"><a href="#note-\1">[\1]</a></sup>', text)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_p(p: str) -> str:
    return linkify_refs(esc(p))


def normalize_title(t: str) -> str:
    return t.title() if t.isupper() else t


def load_lang_data(lang: str) -> dict:
    if lang == "la":
        chapters = []
        for idx, i in enumerate(range(8, 15)):
            tr = json.loads((DATA / "translated" / f"section_{i}.json").read_text(encoding="utf-8"))
            chapters.append({
                "id": f"chap-{idx}",
                "title": normalize_title(tr["title"]),
                "paragraphs": tr["paragraphs_la"],
            })
        return {"lang": "la", "chapters": chapters, "notes": []}
    norm = json.loads((DATA / f"normalized-{lang}.json").read_text(encoding="utf-8"))
    chapters = [
        {
            "id": f"chap-{i}",
            "title": normalize_title(ch["title"]),
            "paragraphs": ch["paragraphs"],
        }
        for i, ch in enumerate(norm["chapters"])
    ]
    return {"lang": lang, "chapters": chapters, "notes": norm["notes"]}


def render_chapters_html(vern_data: dict | None, la_data: dict, lang: str) -> str:
    """Pré-rend HTML : si vern_data, deux colonnes; sinon latin seul."""
    pieces = []
    for ci, lchap in enumerate(la_data["chapters"]):
        vchap = vern_data["chapters"][ci] if vern_data else None
        rows = []
        for pi, lp in enumerate(lchap["paragraphs"]):
            vp = vchap["paragraphs"][pi] if vchap else None
            if vchap:
                rows.append(
                    f'<div class="row">'
                    f'<p class="vern" lang="{lang}">{render_p(vp)}</p>'
                    f'<p class="la" lang="la">{render_p(lp)}</p>'
                    f'</div>'
                )
            else:
                rows.append(f'<div class="row"><p class="la" lang="la">{render_p(lp)}</p></div>')
        titles = ""
        if vchap:
            titles = (
                f'<div class="chap-titles">'
                f'<h2 class="vern" lang="{lang}">{esc(vchap["title"])}</h2>'
                f'<h2 class="la" lang="la">{esc(lchap["title"])}</h2>'
                f'</div>'
            )
        else:
            titles = f'<div class="chap-titles"><h2 class="la" lang="la">{esc(lchap["title"])}</h2></div>'
        pieces.append(
            f'<section id="chap-{ci}" class="chapter">{titles}{"".join(rows)}</section>'
        )
    return "\n".join(pieces)


def render_notes_html(notes: list[str], lang: str) -> str:
    if not notes:
        return ""
    items = []
    for note in notes:
        m = re.match(r"^\[(\d+)\]\s*(.*)$", note)
        if m:
            num, body = m.group(1), m.group(2)
            items.append(f'<li id="note-{num}"><span class="num">[{num}]</span> {esc(body)}</li>')
        else:
            items.append(f"<li>{esc(note)}</li>")
    return (
        f'<section id="notes" class="chapter notes">'
        f'<h2>{esc(NOTES_LABEL.get(lang, "Notes"))}</h2>'
        f'<ol class="notes-list">{"".join(items)}</ol>'
        f'</section>'
    )


def render_toc_html(la_data: dict, vern_data: dict | None, lang: str) -> str:
    items = []
    for ci, lchap in enumerate(la_data["chapters"]):
        title = vern_data["chapters"][ci]["title"] if vern_data else lchap["title"]
        items.append(f'<li><a href="#chap-{ci}">{esc(title)}</a></li>')
    items.append(f'<li><a href="#notes">{esc(NOTES_LABEL.get(lang, "Notes"))}</a></li>')
    return f'<h2 id="toc-title">{esc(TOC_TITLE.get(lang, "Index"))}</h2><ol class="toc-list" id="toc-list">{"".join(items)}</ol>'


def hreflang_tags(current_lang: str) -> str:
    tags = []
    for lang in ALL_LANGS:
        href = f"{DOMAIN}/{lang}/"
        tags.append(f'<link rel="alternate" hreflang="{lang}" href="{href}">')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/">')
    return "\n  ".join(tags)


def jsonld(lang: str, la_data: dict, vern_data: dict | None) -> str:
    chapters = (vern_data or la_data)["chapters"]
    has_part = [
        {
            "@type": "Chapter",
            "@id": f"{DOMAIN}/{lang}/#chap-{i}",
            "name": ch["title"],
            "position": i + 1,
        }
        for i, ch in enumerate(chapters)
    ]
    data = {
        "@context": "https://schema.org",
        "@type": ["Article", "Book"],
        "name": "Magnifica Humanitas",
        "alternateName": "Litterae Encyclicae Magnifica Humanitas",
        "headline": TITLES[lang],
        "description": DESCRIPTIONS[lang],
        "inLanguage": lang,
        "datePublished": "2026-05-15",
        "dateCreated": "2026-05-15",
        "url": f"{DOMAIN}/{lang}/",
        "mainEntityOfPage": f"{DOMAIN}/{lang}/",
        "author": {
            "@type": "Person",
            "name": "Leo XIV",
            "alternateName": "Pope Leo XIV / Léon XIV / Leone XIV",
            "jobTitle": "Pope",
            "sameAs": [
                "https://www.vatican.va/content/leo-xiv/",
                "https://en.wikipedia.org/wiki/Pope_Leo_XIV",
            ],
        },
        "publisher": {
            "@type": "Organization",
            "name": "Libreria Editrice Vaticana",
            "url": "https://www.vatican.va/",
        },
        "genre": ["Encyclical", "Catholic social teaching", "Papal encyclical"],
        "about": [
            {"@type": "Thing", "name": "Artificial intelligence"},
            {"@type": "Thing", "name": "Human dignity"},
            {"@type": "Thing", "name": "Catholic social doctrine"},
        ],
        "isPartOf": {
            "@type": "CreativeWorkSeries",
            "name": "Encyclicals of Pope Leo XIV",
        },
        "hasPart": has_part,
        "image": f"{DOMAIN}/assets/og-image.png",
    }
    return json.dumps(data, ensure_ascii=False)


def keywords(lang: str) -> str:
    base = "Magnifica Humanitas, Leo XIV, Léon XIV, encyclical, encyclique, encíclica, enciclica, Enzyklika, encyklika, intelligence artificielle, artificial intelligence, inteligência artificial, inteligencia artificial, intelligenza artificiale, künstliche Intelligenz, sztuczna inteligencja, Vatican, vatican.va, latin, latina, versio latina, Vulgate, doctrine sociale, Catholic social doctrine, Holy See"
    return base


def render_page(lang: str, all_data: dict[str, dict]) -> str:
    la_data = all_data["la"]
    vern_data = all_data[lang] if lang != "la" else None

    chapters_html = render_chapters_html(vern_data, la_data, lang)
    notes_html = render_notes_html(
        (vern_data or la_data).get("notes", []), lang
    )
    toc_html = render_toc_html(la_data, vern_data, lang)

    selector_options = "\n        ".join(
        f'<option value="{l}"{" selected" if l == lang else ""}>{LANG_LABELS[l]}</option>'
        for l in ALL_LANGS
    )

    mode_both, mode_vern, mode_la = MODE_LABELS.get(lang, MODE_LABELS["en"])
    body_class = "mode-la" if lang == "la" else ""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(TITLES[lang])}</title>
  <meta name="description" content="{esc(DESCRIPTIONS[lang])}">
  <meta name="keywords" content="{esc(keywords(lang))}">
  <meta name="author" content="Pope Leo XIV">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="google-site-verification" content="m3Pxqw2rw3S3dP739bj4H6l_BxJGyAnJC31JIDRv2gc">
  <link rel="canonical" href="{DOMAIN}/{lang}/">
  {hreflang_tags(lang)}
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(TITLES[lang])}">
  <meta property="og:description" content="{esc(DESCRIPTIONS[lang])}">
  <meta property="og:url" content="{DOMAIN}/{lang}/">
  <meta property="og:image" content="{DOMAIN}/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="Magnifica Humanitas">
  <meta property="og:locale" content="{lang}">
  <meta property="article:published_time" content="2026-05-15">
  <meta property="article:author" content="Pope Leo XIV">
  <meta property="article:section" content="Encyclical">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(TITLES[lang])}">
  <meta name="twitter:description" content="{esc(DESCRIPTIONS[lang])}">
  <meta name="twitter:image" content="{DOMAIN}/assets/og-image.png">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/style.css">
  <script type="application/ld+json">{jsonld(lang, la_data, vern_data)}</script>
</head>
<body class="{body_class}">
  <header class="masthead">
    <div class="container">
      <p class="eyebrow">Litterae Encyclicae · Leo PP. XIV · MMXXVI</p>
      <h1>Magnifica Humanitas</h1>
      <p class="subtitle"><em>{esc(SUBTITLES["la"])}</em></p>
      <p class="subtitle-fr" id="subtitle-vern">{esc(SUBTITLES[lang])}</p>
      <p class="date">Romae, apud Sanctum Petrum · die XV mensis Maii anno MMXXVI</p>
    </div>
  </header>

  <div class="controls container">
    <div class="lang-picker">
      <label for="vern-select">{esc(PICKER_LABEL[lang])}</label>
      <select id="vern-select" onchange="window.location.href='/'+this.value+'/'">
        {selector_options}
      </select>
    </div>
    <div class="lang-toggle" role="group" aria-label="Display mode">
      <button data-mode="both" class="{'' if lang == 'la' else 'active'}">{esc(mode_both)}</button>
      <button data-mode="vern"{' style="display:none"' if lang == 'la' else ''}>{esc(mode_vern)}</button>
      <button data-mode="la" class="{'active' if lang == 'la' else ''}">{esc(mode_la)}</button>
    </div>
  </div>

  <nav class="toc container" aria-label="Index">
    {toc_html}
  </nav>

  <main class="container" id="main">
    {chapters_html}
    {notes_html}
  </main>

  <footer>
    <div class="container">
      <p>{('Texte officiel : ' if lang == 'fr' else 'Official text: ')}© Libreria Editrice Vaticana — <a href="https://www.vatican.va/content/leo-xiv/{lang if lang != 'la' else 'la'}/encyclicals/documents/20260515-magnifica-humanitas.html" rel="noopener">vatican.va</a></p>
      <p>{('Traduction latine : œuvre dérivée non officielle (Claude Sonnet 4.6), aucune valeur magistérielle.' if lang == 'fr' else 'Latin translation: unofficial derivative work (Claude Sonnet 4.6), no magisterial value.')}</p>
      <p class="small">Source : <a href="https://github.com/thibpic/magnifica-humanitas">github.com/thibpic/magnifica-humanitas</a></p>
    </div>
  </footer>

  <script src="/assets/app.js" defer></script>
</body>
</html>
"""


def render_root_index() -> str:
    """Page racine = redirige selon Accept-Language vers /fr/ par défaut, et liste les langues."""
    links = "".join(
        f'<li><a href="/{l}/" hreflang="{l}">{LANG_LABELS[l]}</a></li>'
        for l in ALL_LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magnifica Humanitas — Encyclical of Pope Leo XIV (multilingual edition)</title>
  <meta name="description" content="Encyclical Magnifica Humanitas by Pope Leo XIV (15 May 2026) on the protection of the human person in the age of artificial intelligence. Bilingual edition: 7 vernacular languages + Latin.">
  <link rel="canonical" href="{DOMAIN}/">
  <meta name="google-site-verification" content="m3Pxqw2rw3S3dP739bj4H6l_BxJGyAnJC31JIDRv2gc">
  {hreflang_tags("en")}
  <meta property="og:type" content="website">
  <meta property="og:title" content="Magnifica Humanitas — Multilingual Edition">
  <meta property="og:description" content="Pope Leo XIV's encyclical on AI and human dignity, in 7 languages + Latin.">
  <meta property="og:url" content="{DOMAIN}/">
  <meta property="og:image" content="{DOMAIN}/assets/og-image.png">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=EB+Garamond&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/style.css">
  <style>
    .lang-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; max-width:600px; margin:3rem auto; padding:0; list-style:none; }}
    .lang-grid a {{ display:block; padding:1.2rem; text-align:center; border:1px solid var(--rule); border-radius:4px; background:var(--bg-elev); color:var(--ink); text-decoration:none; font-family:var(--display); font-size:1.2rem; transition:all .2s; }}
    .lang-grid a:hover {{ border-color:var(--accent); color:var(--accent); transform:translateY(-2px); box-shadow:var(--shadow); }}
  </style>
  <script>
    (function() {{
      try {{
        var saved = localStorage.getItem("mh.vern");
        if (saved && ["fr","en","es","it","de","pt","pl","la"].indexOf(saved) >= 0) {{
          window.location.replace("/" + saved + "/");
          return;
        }}
        var nav = (navigator.language || "en").slice(0, 2).toLowerCase();
        if (["fr","en","es","it","de","pt","pl"].indexOf(nav) >= 0) {{
          window.location.replace("/" + nav + "/");
        }}
      }} catch (_) {{}}
    }})();
  </script>
</head>
<body>
  <header class="masthead">
    <div class="container">
      <p class="eyebrow">Litterae Encyclicae · Leo PP. XIV · MMXXVI</p>
      <h1>Magnifica Humanitas</h1>
      <p class="subtitle"><em>De persona humana tuenda aetate intellegentiae artificialis</em></p>
      <p class="subtitle-fr">Encyclical of Pope Leo XIV · 15 May 2026 · on AI and human dignity</p>
    </div>
  </header>
  <main class="container">
    <h2 style="text-align:center;font-family:var(--display);color:var(--accent);letter-spacing:.2em;text-transform:uppercase;font-size:.9rem;margin-top:3rem">Choose a language · Elige una lengua · Wählen Sie eine Sprache</h2>
    <ul class="lang-grid">
      {links}
    </ul>
  </main>
  <footer>
    <div class="container">
      <p>© Libreria Editrice Vaticana — <a href="https://www.vatican.va/">vatican.va</a> · Source: <a href="https://github.com/thibpic/magnifica-humanitas">github.com/thibpic/magnifica-humanitas</a></p>
    </div>
  </footer>
</body>
</html>
"""


def render_sitemap() -> str:
    urls = [(DOMAIN + "/", "1.0")]
    urls += [(f"{DOMAIN}/{lang}/", "0.9") for lang in ALL_LANGS]
    body = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>2026-05-28</lastmod><changefreq>monthly</changefreq><priority>{p}</priority></url>"
        for loc, p in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def render_robots() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""


def render_favicon_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="8" fill="#6e1c1c"/>
  <text x="32" y="46" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="44" font-weight="600" fill="#fbf6e8">MH</text>
</svg>
"""


def render_og_image_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f1e9d5"/>
      <stop offset="1" stop-color="#f7f3ea"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <text x="600" y="160" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="22" letter-spacing="6" fill="#6e1c1c">LITTERAE ENCYCLICAE · LEO PP. XIV · MMXXVI</text>
  <text x="600" y="320" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="120" font-weight="600" fill="#1c1410">Magnifica Humanitas</text>
  <text x="600" y="400" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="36" font-style="italic" fill="#4a3a2e">De persona humana tuenda aetate intellegentiae artificialis</text>
  <text x="600" y="460" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="26" font-style="italic" fill="#4a3a2e">Édition bilingue · Bilingual edition · Edizione bilingue</text>
  <line x1="450" y1="510" x2="750" y2="510" stroke="#a04444" stroke-width="1"/>
  <text x="600" y="555" text-anchor="middle" font-family="Georgia, Palatino, serif" font-size="22" letter-spacing="3" fill="#6e1c1c">magnifica-humanitas.lat</text>
</svg>
"""


def main():
    # Charge toutes les langues
    all_data = {lang: load_lang_data(lang) for lang in ALL_LANGS}

    # JSON data (toujours utile au cas où un JS dynamique veut switcher)
    for lang, d in all_data.items():
        (DOCS_DATA / f"{lang}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    # Pages statiques par langue
    for lang in ALL_LANGS:
        out_dir = DOCS / lang
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(render_page(lang, all_data), encoding="utf-8")
        print(f"  {lang}/index.html")

    # Racine
    (DOCS / "index.html").write_text(render_root_index(), encoding="utf-8")
    # sitemap + robots
    (DOCS / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")
    (DOCS / "robots.txt").write_text(render_robots(), encoding="utf-8")
    # assets
    assets = DOCS / "assets"
    (assets / "favicon.svg").write_text(render_favicon_svg(), encoding="utf-8")
    og_svg = render_og_image_svg()
    (assets / "og-image.svg").write_text(og_svg, encoding="utf-8")
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=og_svg.encode("utf-8"),
                         write_to=str(assets / "og-image.png"),
                         output_width=1200, output_height=630)
        print("  og-image.png (rendered)")
    except Exception as e:
        print(f"  og-image.png: {e}")
    print(f"  index.html, sitemap.xml, robots.txt, favicon.svg, og-image.svg")


if __name__ == "__main__":
    main()
