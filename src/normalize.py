"""Normalise les JSON multi-langues : ne garde que les 7 sections de corps + notes,
toutes indexées 0..6 (corps) et 'notes' (références)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["fr", "en", "es", "it", "de", "pt", "pl"]
EXPECTED = [20, 37, 56, 50, 66, 63, 22]


def find_body(sections):
    """Trouve la séquence contiguë de 7 sections aux comptes [20,37,56,50,66,63,22]."""
    counts = [len(s["paragraphs"]) for s in sections]
    for i in range(len(counts) - 6):
        if counts[i : i + 7] == EXPECTED:
            return i
    raise ValueError(f"Séquence introuvable, counts={counts}")


def main():
    for lang in LANGS:
        path = ROOT / "data" / f"magnifica-{lang}.json"
        if not path.exists():
            continue
        sections = json.loads(path.read_text(encoding="utf-8"))
        start = find_body(sections)
        body = sections[start : start + 7]
        # Notes : section juste après le corps (la plus longue restante, typiquement 225+ paragraphes)
        notes = []
        for s in sections[start + 7 :]:
            if len(s["paragraphs"]) > 100:
                notes = s["paragraphs"]
                break
        out = {
            "lang": lang,
            "chapters": body,
            "notes": notes,
        }
        out_path = ROOT / "data" / f"normalized-{lang}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{lang}] start={start}, 7 chapitres, {len(notes)} notes")


if __name__ == "__main__":
    main()
