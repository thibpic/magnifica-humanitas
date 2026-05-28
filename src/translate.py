"""Traduit l'encyclique en latin ecclésiastique via l'API Anthropic.

Traite en parallèle (ThreadPool) section par section. Sortie : magnifica-la.json
parallèle à magnifica-fr.json, paragraphe par paragraphe (même indexation).
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "magnifica-fr.json"
OUT = ROOT / "data" / "magnifica-la.json"
MODEL = "claude-sonnet-4-6"

# Indices des sections à traduire (corps de l'encyclique). 0-7 = TOC, 15 = notes.
CONTENT_INDICES = list(range(8, 15))
# Les notes (15) : on les laisse en français (références bibliographiques).

SYSTEM = """Tu es un latiniste expert en latin ecclésiastique classique, formé à la \
tradition vaticane (style des encycliques publiées en latin sur vatican.va). \
Tu traduis fidèlement du français vers le latin ecclésiastique soigné.

Règles :
- Conserve la structure paragraphe par paragraphe exactement.
- Style : latin ecclésiastique de la Curie romaine, syntaxe classique soutenue.
- Garde tels quels (sans traduction) : noms propres, citations latines déjà \
présentes (Magnifica Humanitas, Rerum Novarum, Gaudium et Spes, etc.), \
références bibliographiques.
- Les citations bibliques peuvent être rendues par la Vulgate quand évident.
- Format de sortie : JSON strict, un tableau de chaînes, dans le MÊME ordre et \
le MÊME nombre que les paragraphes en entrée. Aucun commentaire, aucun texte \
hors JSON. Échappe correctement les guillemets.
"""

PROMPT_TEMPLATE = """Traduis en latin ecclésiastique les {n} paragraphes suivants, \
issus de la section « {title} » de l'encyclique Magnifica Humanitas.

Réponds UNIQUEMENT par un tableau JSON de {n} chaînes, dans l'ordre.

Paragraphes (JSON):
{paragraphs}
"""


def translate_section(client: Anthropic, idx: int, section: dict) -> list[str]:
    paragraphs = section["paragraphs"]
    n = len(paragraphs)
    prompt = PROMPT_TEMPLATE.format(
        n=n,
        title=section["title"],
        paragraphs=json.dumps(paragraphs, ensure_ascii=False, indent=2),
    )
    t0 = time.time()
    text_parts: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=32000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            text_parts.append(chunk)
    text = "".join(text_parts).strip()
    # Strip code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:].lstrip()
    # Parser : trouve le premier '[' et le dernier ']'
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"Section {idx}: pas de JSON détecté\n{text[:500]}")
    arr = json.loads(text[start : end + 1])
    if len(arr) != n:
        print(f"  WARN section {idx}: {len(arr)} paragraphes traduits / {n} attendus")
    dt = time.time() - t0
    print(f"  ✓ section {idx} ({section['title'][:40]}) — {n}p en {dt:.1f}s")
    return arr


def main():
    sections = json.loads(SRC.read_text(encoding="utf-8"))
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Charge l'existant pour reprise éventuelle.
    out: dict[int, list[str]] = {}
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        out = {int(k): v for k, v in existing.items()}
        print(f"Reprise : {len(out)} sections déjà traduites.")

    todo = [i for i in CONTENT_INDICES if i not in out]
    print(f"À traduire : {todo}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(translate_section, client, i, sections[i]): i for i in todo
        }
        for f in as_completed(futures):
            i = futures[f]
            try:
                out[i] = f.result()
                # Sauvegarde incrémentale
                OUT.write_text(
                    json.dumps({str(k): v for k, v in out.items()}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception as e:
                print(f"  ✗ section {i}: {e}")
                sys.exit(1)

    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
