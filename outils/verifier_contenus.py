"""Vérifie qu'un fichier de contenus (calendrier ou propositions) respecte la fiche marque.

Utilisation :
    python3 outils/verifier_contenus.py propositions/2026-11-30/propositions.csv --marque da-laura
    python3 outils/verifier_contenus.py ... --attendu reels=3,posts=5,stories=7

Contrôles (posts, carrousels et réels) : 2 à 4 emojis, 5 à 10 hashtags, #DaLaura en premier,
hashtags tous présents dans la fiche, mention loi Évin si du vin ou de l'alcool est évoqué.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐]")
ALCOOL = re.compile(r"\b(vin|vino|prosecco|spritz|champagne|cocktail|grappa|limoncello|bière)\b", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--marque", default="da-laura")
    ap.add_argument("--attendu", help="ex. reels=3,posts=5,stories=7")
    a = ap.parse_args()
    fiche = (RACINE / "marques" / f"{a.marque}.md").read_text(encoding="utf-8")
    tags_fiche = set(re.findall(r"#\w+", fiche))
    marque_tag = re.findall(r"\*\*Hashtags? de marque :\*\*\s*(#\w+)", fiche)
    with open(RACINE / a.csv if not Path(a.csv).is_absolute() else a.csv, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))

    erreurs, n = [], {"reels": 0, "posts": 0, "stories": 0}
    for r in rows:
        f = r["Format"]
        if f.startswith("Story"):
            n["stories"] += 1
            continue
        n["reels" if f == "Réel" else "posts"] += 1
        ref = f"{r['Date']} {f} « {r.get('Texte visuel', '')} »"
        e = len(EMOJI.findall(r["Légende"]))
        tags = r["Hashtags"].split()
        if not 2 <= e <= 4:
            erreurs.append(f"{ref} : {e} emojis (attendu 2 à 4)")
        if not 5 <= len(tags) <= 10:
            erreurs.append(f"{ref} : {len(tags)} hashtags (attendu 5 à 10)")
        if marque_tag and (not tags or tags[0] != marque_tag[0]):
            erreurs.append(f"{ref} : le hashtag de marque {marque_tag[0]} doit être en premier")
        hors = set(tags) - tags_fiche
        if hors:
            erreurs.append(f"{ref} : hashtags absents de la fiche : {' '.join(sorted(hors))}")
        if ALCOOL.search(r["Légende"]) and "abus d'alcool" not in r["Légende"]:
            erreurs.append(f"{ref} : alcool évoqué sans la mention loi Évin")
    if a.attendu:
        for paire in a.attendu.split(","):
            k, v = paire.split("=")
            if n.get(k) != int(v):
                erreurs.append(f"Nombre de {k} : {n.get(k)} (attendu {v})")
    print(f"{n['reels']} réels, {n['posts']} posts, {n['stories']} stories.")
    if erreurs:
        print("À corriger :\n- " + "\n- ".join(erreurs))
        sys.exit(1)
    print("Tout respecte la fiche marque.")


if __name__ == "__main__":
    main()
