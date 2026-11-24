"""Construit (ou met à jour) le calendrier de programmation calendriers/dalaura-AAAA-MM.csv.

Utilisation :
    python3 outils/construire_programmation.py 2026-12

Sources :
- posts et réels : calendriers/da-laura-AAAA-MM.csv (calendrier éditorial), avec les visuels de
  publications/da-laura/ et les vidéos de reels/da-laura/ ;
- stories : les stories « Piatti del giorno » de stories/da-laura/plats-du-jour/AAAA-MM/
  (ou, à défaut, de la proposition stories/da-laura/plats-du-jour/proposition-AAAA-MM/).

Les statuts déjà saisis (validé client, programmé, publié) sont CONSERVÉS : relancer le script ne
remet jamais un contenu à « à créer ».
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from programmation import RACINE, ecrire, lire  # noqa: E402

HEURE_STORY = "11:00"
CONTRAT = {"post": 8, "story": 20, "reel": 2}


def heure(h):
    h = h.strip().replace("h", ":")
    hh, mm = (h.split(":") + ["00"])[:2]
    return f"{int(hh):02d}:{int(mm or 0):02d}"


def main(mois):
    a, m = mois.split("-")
    edito = RACINE / "calendriers" / f"da-laura-{mois}.csv"
    sortie = RACINE / "calendriers" / f"dalaura-{mois}.csv"
    anciens = {}
    if sortie.exists():
        for l in lire(sortie):
            anciens.setdefault((l["date"], l["format"]), []).append(l)

    lignes = []
    with open(edito, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            if r["Format"].startswith("Story"):
                continue
            j, mo, an = r["Date"].split("/")
            date = f"{an}-{mo}-{j}"
            if r["Format"] == "Réel":
                videos = sorted((RACINE / "reels" / "da-laura").glob(f"{date}-*.mp4"))
                f = videos[0] if videos else None
                leg = f.with_suffix(".txt").read_text(encoding="utf-8").strip() if f else ""
                lignes.append({"date": date, "heure": heure(r["Heure"]), "format": "reel",
                               "fichier": str(f.relative_to(RACINE)) if f else "", "légende": leg})
            else:
                dossiers = sorted((RACINE / "publications" / "da-laura").glob(f"{date}-*"))
                d = dossiers[0] if dossiers else None
                visuels = sorted(d.glob("visuel-*.jpg")) if d else []
                leg = (d / "legende.txt").read_text(encoding="utf-8").strip() if d else ""
                lignes.append({"date": date, "heure": heure(r["Heure"]), "format": "post",
                               "fichier": " + ".join(str(v.relative_to(RACINE)) for v in visuels), "légende": leg})

    dossier_s = RACINE / "stories" / "da-laura" / "plats-du-jour" / mois
    if not any(dossier_s.glob("*.jpg")):
        dossier_s = RACINE / "stories" / "da-laura" / "plats-du-jour" / f"proposition-{mois}"
    for img in sorted(dossier_s.glob(f"{a}-{m}-*.jpg")):
        txt = img.with_suffix(".txt").read_text(encoding="utf-8") if img.with_suffix(".txt").exists() else ""
        plats = [l[2:].strip() for l in txt.splitlines() if l.startswith("- ")]
        leg = "Story « Piatti del giorno » : " + " / ".join(plats) + \
              ". À ajouter : sticker Lien vers la réservation, sticker Lieu Cannes."
        lignes.append({"date": img.stem, "heure": HEURE_STORY, "format": "story",
                       "fichier": str(img.relative_to(RACINE)), "légende": leg})

    # statuts conservés (même date et même format, dans l'ordre)
    vus = {}
    for l in lignes:
        k = (l["date"], l["format"])
        i = vus.get(k, 0)
        vus[k] = i + 1
        ancien = anciens.get(k, [])
        l["statut"] = ancien[i]["statut"] if i < len(ancien) else "à créer"
        if i < len(ancien) and ancien[i]["statut"] != "à créer":
            # contenu déjà validé : on garde aussi l'heure, le fichier et la légende validés
            l.update({c: ancien[i][c] for c in ("heure", "fichier", "légende")})
    lignes.sort(key=lambda l: (l["date"], l["heure"]))
    ecrire(sortie, lignes)

    n = {f: sum(l["format"] == f for l in lignes) for f in CONTRAT}
    print(f"{sortie.relative_to(RACINE)} : {n['post']} posts, {n['story']} stories, {n['reel']} réels.")
    for f, attendu in CONTRAT.items():
        if n[f] != attendu:
            print(f"⚠️ Contrat Essentielle : {attendu} {f}s attendus, {n[f]} dans le calendrier.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-12")
