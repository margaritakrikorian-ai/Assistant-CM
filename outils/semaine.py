"""Prépare les propositions de contenu de la semaine : rassemble tout le contexte utile.

Utilisation (depuis la racine du projet) :
    python3 outils/semaine.py                      # marque da-laura, semaine du lundi qui vient
    python3 outils/semaine.py da-laura --lundi 2026-11-30
    python3 outils/semaine.py da-laura --terminer  # après validation de la génération : note la date

Crée propositions/<lundi>/contexte.md avec :
- la fiche marque à appliquer ;
- les NOUVELLES photos (ajoutées depuis la dernière proposition) et les autres photos disponibles ;
- la veille du ou des mois concernés ;
- les dernières statistiques Instagram (meilleures publications, moyennes par format) ;
- ce que prévoit déjà le calendrier éditorial cette semaine-là (pour compléter, pas doublonner).
"""
import argparse
import csv
import datetime
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MEDIAS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".mp4", ".mov"}
HISTORIQUE = RACINE / "propositions" / "historique.csv"


def lundi_suivant(aujourd_hui=None):
    d = aujourd_hui or datetime.date.today()
    return d + datetime.timedelta(days=(7 - d.weekday()) % 7 or 7) if d.weekday() else d


def date_ajout(fichier):
    """Date d'ajout dans Git (premier commit) ; maintenant si le fichier n'est pas encore commité."""
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--format=%cI", "--", str(fichier)],
                             cwd=RACINE, capture_output=True, text=True, timeout=30).stdout.split()
        if out:
            return datetime.datetime.fromisoformat(out[-1])
    except Exception:
        pass
    return datetime.datetime.now(datetime.timezone.utc)


def derniere_execution(marque):
    if not HISTORIQUE.exists():
        return None
    with open(HISTORIQUE, encoding="utf-8-sig") as fh:
        lignes = [r for r in csv.DictReader(fh, delimiter=";") if r["Marque"] == marque]
    return datetime.datetime.fromisoformat(lignes[-1]["Généré le"]) if lignes else None


def resume_stats(marque):
    dossier = RACINE / "stats" / marque
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        return ["Aucune statistique disponible (lancer `python3 outils/stats_instagram.py " + marque +
                "` ou déposer un export Meta Business Suite dans `stats/" + marque + "/`)."]
    f = fichiers[-1]
    with open(f, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))

    def score(r):
        for k in ("Interactions", "J'aime"):
            try:
                return float(r.get(k) or 0) + (float(r.get("Commentaires") or 0) if k == "J'aime" else 0)
            except ValueError:
                continue
        return 0

    out = [f"Source : `{f.relative_to(RACINE)}` ({len(rows)} publications)", "", "**Top 5 des publications :**", ""]
    for r in sorted(rows, key=score, reverse=True)[:5]:
        out.append(f"- {r.get('Date', '')} · {r.get('Format', '')} · score {score(r):.0f} · "
                   f"{(r.get('Légende') or '')[:90]}… ({r.get('Lien', '')})")
    par_format = {}
    for r in rows:
        par_format.setdefault(r.get("Format") or "?", []).append(score(r))
    out += ["", "**Moyenne par format :**", ""]
    out += [f"- {k} : {sum(v) / len(v):.0f} ({len(v)} publications)" for k, v in par_format.items()]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("marque", nargs="?", default="da-laura")
    ap.add_argument("--lundi", help="lundi de la semaine visée (AAAA-MM-JJ) ; défaut : le lundi qui vient")
    ap.add_argument("--terminer", action="store_true", help="enregistre la proposition dans l'historique")
    a = ap.parse_args()
    lundi = datetime.date.fromisoformat(a.lundi) if a.lundi else lundi_suivant()
    jours = [lundi + datetime.timedelta(days=i) for i in range(7)]
    dossier = RACINE / "propositions" / lundi.isoformat()

    if a.terminer:
        HISTORIQUE.parent.mkdir(parents=True, exist_ok=True)
        neuf = not HISTORIQUE.exists()
        with open(HISTORIQUE, "a", newline="", encoding="utf-8-sig" if neuf else "utf-8") as fh:
            w = csv.writer(fh, delimiter=";")
            if neuf:
                w.writerow(["Marque", "Semaine", "Généré le", "Dossier"])
            w.writerow([a.marque, lundi.isoformat(), datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                        str(dossier.relative_to(RACINE))])
        print(f"Proposition de la semaine du {lundi:%d/%m/%Y} enregistrée dans l'historique.")
        return

    dossier.mkdir(parents=True, exist_ok=True)
    fiche = RACINE / "marques" / f"{a.marque}.md"
    depuis = derniere_execution(a.marque)

    photos = sorted(p for p in (RACINE / "photos" / a.marque).rglob("*") if p.suffix.lower() in MEDIAS)
    nouvelles, anciennes = [], []
    for p in photos:
        (nouvelles if depuis is None or date_ajout(p) > depuis else anciennes).append(p.relative_to(RACINE))

    mois = sorted({f"{j.year}-{j.month:02d}" for j in jours})
    veilles = [RACINE / "veille" / f"{m}.md" for m in mois]

    prevu = []
    for m in mois:
        cal = RACINE / "calendriers" / f"{a.marque}-{m}.csv"
        if cal.exists():
            with open(cal, encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh, delimiter=";"):
                    d = datetime.datetime.strptime(r["Date"], "%d/%m/%Y").date()
                    if d in jours and not r["Format"].startswith("Story"):
                        prevu.append(f"- {r['Jour']} {r['Date']} · {r['Heure']} · {r['Format']} · {r['Texte visuel']}")

    L = [f"# Contexte : semaine du {lundi:%d/%m/%Y} au {jours[-1]:%d/%m/%Y} ({a.marque})", ""]
    L += ["## Fiche marque", "", f"`{fiche.relative_to(RACINE)}`" + ("" if fiche.exists() else " **(introuvable)**"), ""]
    L += ["## Photos", "",
          "Dernière proposition : " + (f"{depuis:%d/%m/%Y %H:%M} UTC" if depuis else "aucune (toutes les photos sont nouvelles)"), "",
          f"**Nouvelles photos ({len(nouvelles)}) : à utiliser en priorité**", ""]
    L += [f"- `{p}`" for p in nouvelles] or ["- (aucune)"]
    L += ["", f"**Autres photos disponibles ({len(anciennes)})**", ""]
    L += [f"- `{p}`" for p in anciennes[:60]] or ["- (aucune)"]
    if len(anciennes) > 60:
        L.append(f"- … et {len(anciennes) - 60} autres")
    L += ["", "## Veille", ""]
    L += [f"- `{v.relative_to(RACINE)}`" + ("" if v.exists() else " **(absente : faire la veille avant de proposer)**")
          for v in veilles]
    L += ["", "## Statistiques Instagram", ""] + resume_stats(a.marque)
    L += ["", "## Déjà prévu au calendrier cette semaine", ""] + (prevu or ["- (rien : pas de calendrier pour cette période)"])
    (dossier / "contexte.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n→ Contexte enregistré dans {(dossier / 'contexte.md').relative_to(RACINE)}")


if __name__ == "__main__":
    main()
