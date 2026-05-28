# Magnifica Humanitas — Versio Latina

Édition bilingue **français · latin** de l'encyclique *Magnifica Humanitas* du pape Léon XIV (15 mai 2026), sur la protection de la personne humaine à l'ère de l'intelligence artificielle.

🌐 **Site publié** : https://thibpic.github.io/magnifica-humanitas/

## Contenu

- Texte français : version officielle de la Libreria Editrice Vaticana ([vatican.va](https://www.vatican.va/content/leo-xiv/fr/encyclicals/documents/20260515-magnifica-humanitas.html)).
- Texte latin : traduction non officielle générée par modèle de langue (Claude Sonnet 4.6) en latin ecclésiastique. **Aucune valeur magistérielle** — œuvre d'étude et de lecture liturgique privée.

## Architecture

```
data/
  magnifica-fr.html         # source Vatican
  magnifica-fr.json         # texte structuré par sections
  sections/section_N.json   # découpage par section pour traduction
  translated/section_N.json # traductions latines
src/
  extract.py                # HTML Vatican -> JSON structuré
  translate.py              # script API Anthropic (parallèle)
  build_site.py             # JSON -> site HTML statique
docs/
  index.html                # site publié via GitHub Pages
  assets/style.css          # typographie Cormorant / EB Garamond
  assets/app.js             # bascule FR / LA / FR+LA
```

## Reconstruire

```bash
python3 -m venv .venv && .venv/bin/pip install beautifulsoup4 lxml anthropic
.venv/bin/python src/extract.py
.venv/bin/python src/translate.py
.venv/bin/python src/build_site.py
```

## Licence

- Texte français : © Libreria Editrice Vaticana.
- Code & traduction latine dérivée : libre usage à des fins d'étude (CC BY-NC 4.0).
