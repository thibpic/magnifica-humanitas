# Magnifica Humanitas — Versio Latina

Édition multilingue de l'encyclique *Magnifica Humanitas* du pape Léon XIV (15 mai 2026), sur la protection de la personne humaine à l'ère de l'intelligence artificielle. Affichage **vernaculaire ↔ latin** en deux colonnes.

🌐 **Site** : https://thibpic.github.io/magnifica-humanitas/
✨ **Domaine cible (à enregistrer)** : `versiolatina.church`

## Langues disponibles

| Côté gauche (vernaculaire) | Côté droit |
| --- | --- |
| Français, English, Español, Italiano, Deutsch, Português, Polski | Latina |

Les sept versions vernaculaires proviennent directement de [vatican.va](https://www.vatican.va/) ; le texte latin est une traduction non officielle générée par modèle de langue (Claude Sonnet 4.6) en latin ecclésiastique. **Aucune valeur magistérielle** — étude et usage liturgique privé.

Toutes les éditions sont alignées paragraphe par paragraphe (7 chapitres, 314 paragraphes).

## Activation du domaine personnalisé

1. Enregistrer `versiolatina.church` (ex. via [Porkbun](https://porkbun.com/), [Gandi](https://www.gandi.net/) — ~25 €/an).
2. Configurer les DNS chez le registrar :
   - Quatre enregistrements **A** sur la racine `@` : `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - Un enregistrement **CNAME** sur `www` : `thibpic.github.io.`
3. Recréer le fichier `docs/CNAME` :
   ```bash
   echo "versiolatina.church" > docs/CNAME && git add docs/CNAME && git commit -m "feat: active domaine versiolatina.church" && git push
   ```
4. Dans **Settings → Pages** du repo GitHub, renseigner le domaine et cocher *Enforce HTTPS* après propagation DNS (15 min à 24 h).

## Architecture

```
data/
  magnifica-<lang>.html       # source Vatican par langue
  magnifica-<lang>.json       # extraction structurée
  normalized-<lang>.json      # 7 chapitres + notes, format unifié
  sections/section_N.json     # découpage FR pour traduction
  translated/section_N.json   # traductions latines (output subagents)
src/
  extract.py                  # HTML Vatican -> JSON
  normalize.py                # extraction des 7 chapitres alignés
  translate.py                # API Anthropic, parallèle (optionnel)
  build_site.py               # JSON -> site
docs/
  index.html                  # shell HTML
  data/<lang>.json            # données chargées dynamiquement
  assets/style.css            # typographie Cormorant / EB Garamond
  assets/app.js               # sélecteur langue + toggle modes
```

## Reconstruire

```bash
python3 -m venv .venv && .venv/bin/pip install beautifulsoup4 lxml anthropic
# 1. Télécharger les 7 langues (si pas déjà en data/)
for lang in fr en es it de pt pl; do
  curl -sL "https://www.vatican.va/content/leo-xiv/$lang/encyclicals/documents/20260515-magnifica-humanitas.html" -o "data/magnifica-$lang.html"
done
# 2. Pipeline
.venv/bin/python src/extract.py
.venv/bin/python src/normalize.py
# (Traduction latine déjà faite dans data/translated/. Pour relancer : src/translate.py)
.venv/bin/python src/build_site.py
```

## Licence

- Texte officiel multilingue : © Libreria Editrice Vaticana.
- Code & traduction latine dérivée : libre usage à des fins d'étude (CC BY-NC 4.0).
