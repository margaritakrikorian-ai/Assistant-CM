"""Prépare le pack « prêt à programmer » : a-programmer/ + a-programmer/RECAP.md.

Utilisation :
    python3 outils/pack_programmation.py

Pour chaque contenu au statut « validé client » (et UNIQUEMENT celui-là) des calendriers
calendriers/dalaura-AAAA-MM.csv :
    a-programmer/<date>-<format>/  visuel(s) au bon format + legende.txt
- post  : visuel.jpg (ou visuel-01.jpg, -02… pour un carrousel) en 1080x1350
- story : story.jpg en 1080x1920
- reel  : reel.mp4 en 1080x1920 (+ couverture.jpg si elle existe)
Le dossier a-programmer/ est entièrement reconstruit à chaque lancement.
"""
import datetime
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from programmation import (ADRESSE, COMPTE, FORMATS, RACINE, TELEPHONE, est_valide_client,  # noqa: E402
                           fichiers, fichiers_calendrier, legende_finale, lire, moment, norm,
                           preparer_image, preparer_video, problemes)

SORTIE = RACINE / "a-programmer"
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]
NOMS = {"post": "Publication", "story": "Story", "reel": "Réel"}


def date_fr(dt):
    return f"{JOURS[dt.weekday()]} {dt.day}{'er' if dt.day == 1 else ''} {MOIS[dt.month - 1]}"


def main():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    prets, bloques, compte = [], [], {}
    for cal in fichiers_calendrier():
        for l in lire(cal):
            s = norm(l["statut"])
            compte[s] = compte.get(s, 0) + 1
            if not est_valide_client(l):
                continue  # seuls les contenus validés par le client entrent dans le pack
            p = problemes(l)
            if p:
                bloques.append((l, p))
                continue
            prets.append(l)
    prets.sort(key=moment)

    noms_pris = set()
    for l in prets:
        fmt = l["format"].strip().lower()
        nom = f"{l['date']}-{fmt}"
        k = 2
        while nom in noms_pris:
            nom = f"{l['date']}-{fmt}-{k}"
            k += 1
        noms_pris.add(nom)
        d = SORTIE / nom
        fs = fichiers(l)
        if fmt == "reel":
            preparer_video(fs[0], d / "reel.mp4")
            couv = fs[0].with_name(fs[0].stem + "-couverture.jpg")
            if couv.exists():
                preparer_image(couv, d / "couverture.jpg", FORMATS["reel"])
            medias = ["reel.mp4"] + (["couverture.jpg"] if couv.exists() else [])
        elif fmt == "story":
            preparer_image(fs[0], d / "story.jpg", FORMATS["story"])
            medias = ["story.jpg"]
        elif len(fs) == 1:
            preparer_image(fs[0], d / "visuel.jpg", FORMATS["post"])
            medias = ["visuel.jpg"]
        else:
            medias = []
            for i, f in enumerate(fs, 1):
                preparer_image(f, d / f"visuel-{i:02d}.jpg", FORMATS["post"])
                medias.append(f"visuel-{i:02d}.jpg")
        if fmt == "story":
            texte = (f"STORY — pas de légende sur Instagram.\n\n{l['légende'].strip()}\n\n"
                     f"Sticker « Lien » : page de réservation\nSticker « Lieu » : Da Laura, Cannes\n"
                     f"Adresse : {ADRESSE}\nRéservations : {TELEPHONE}\n")
        else:
            texte = legende_finale(l) + "\n"
        (d / "legende.txt").write_text(texte, encoding="utf-8")
        l["_dossier"], l["_medias"] = nom, medias

    # ---------- RECAP.md ----------
    R = [f"# À programmer : Da Laura ({COMPTE})", "",
         f"Mis à jour le {datetime.date.today():%d/%m/%Y}. Ce récapitulatif ne contient **que** les contenus au statut "
         "« validé client », triés par date.", "",
         f"**{len(prets)} contenu(s) prêt(s) à programmer**"
         + (f" · ⚠️ {len(bloques)} validé(s) mais bloqué(s) (voir en bas)" if bloques else "") + ".", ""]
    if prets:
        R += ["## Résumé", "", "| ☐ | Date et heure | Format | Dossier |", "|---|---|---|---|"]
        for l in prets:
            R.append(f"| ☐ | {date_fr(moment(l))} à {l['heure']} | {NOMS[l['format'].strip().lower()]} | "
                     f"[`{l['_dossier']}/`]({l['_dossier']}/) |")
        R += ["", "## Comment programmer sur l'iPad (Meta Business Suite)", "",
              "À faire une fois : installez l'application **Meta Business Suite** et connectez-vous au compte qui gère "
              "la page Facebook et le compte Instagram de Da Laura.", "",
              "Pour **chaque** ligne ci-dessous :", "",
              "1. **Enregistrez les fichiers** du dossier dans Photos (l'assistant vous les envoie dans la conversation ; "
              "sinon, sur GitHub : ouvrez le fichier puis « Download »).",
              "2. Dans Meta Business Suite, touchez **Créer** (ou **+**), puis **Publication**, **Story** ou **Reel** selon le format.",
              f"3. Cochez le compte Instagram **{COMPTE}** (et la page Facebook si vous voulez publier aux deux endroits).",
              "4. Ajoutez le ou les visuels **dans l'ordre** (visuel-01, puis visuel-02…).",
              "5. **Copiez-collez la légende** du fichier `legende.txt` (posts et réels ; les stories n'ont pas de légende).",
              "6. Ouvrez les **options de programmation**, choisissez la **date et l'heure** indiquées, puis touchez **Programmer**.",
              "7. Dites ensuite à l'assistant « c'est programmé » : il passera le statut à « programmé ».", "",
              "> ⚠️ Un contenu programmé à la main doit passer au statut **« programmé »** tout de suite : sinon, le jour où la "
              "publication automatique sera activée, il pourrait être publié une deuxième fois.", "",
              "## Détail", ""]
        for l in prets:
            fmt = l["format"].strip().lower()
            R += [f"### {date_fr(moment(l)).capitalize()} à {l['heure']} · {NOMS[fmt]}", "",
                  f"- **Dossier :** [`a-programmer/{l['_dossier']}/`]({l['_dossier']}/)",
                  "- **Fichiers :** " + ", ".join(f"[`{m}`]({l['_dossier']}/{m})" for m in l["_medias"]),
                  f"- **Dans Meta Business Suite :** Créer → {NOMS[fmt]} → {COMPTE} → date {l['date']} à {l['heure']}", ""]
            if fmt == "story":
                R += ["- **Stickers à ajouter :** Lien (réservation) et Lieu (Da Laura, Cannes)", ""]
            else:
                R += ["- **Légende à copier :**", "", "```", legende_finale(l), "```", ""]
    else:
        R += ["Aucun contenu au statut « validé client » pour l'instant. Dès que Laura valide un contenu, son statut passe "
              "à « validé client » dans le calendrier et il apparaît ici.", ""]
    if bloques:
        R += ["## ⚠️ Validés mais bloqués", "", "Ces contenus sont validés mais ne peuvent pas être programmés tels quels :", ""]
        for l, p in bloques:
            R.append(f"- {l['date']} {l['heure']} · {l['format']} : {' ; '.join(p)}")
        R.append("")
    R += ["## Où en est le calendrier", "", "| Statut | Nombre |", "|---|---|"]
    for s in ["a creer", "valide client", "programme", "publie"]:
        lib = {"a creer": "à créer", "valide client": "validé client", "programme": "programmé", "publie": "publié"}[s]
        R.append(f"| {lib} | {compte.get(s, 0)} |")
    (SORTIE / "RECAP.md").write_text("\n".join(R) + "\n", encoding="utf-8")
    print(f"{len(prets)} contenu(s) prêt(s) dans a-programmer/ ; {len(bloques)} bloqué(s). Récapitulatif : a-programmer/RECAP.md")
    for l, p in bloques:
        print(f"⚠️ {l['date']} {l['format']} : {' ; '.join(p)}")


if __name__ == "__main__":
    main()
