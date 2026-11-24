"""Génère les réels (MP4 vertical 1080x1920, 15 à 30 s) d'un calendrier éditorial, avec ffmpeg.

Utilisation (depuis la racine du projet) :
    python3 outils/generer_reels.py calendriers/da-laura-2026-12.csv

Pour chaque ligne « Réel » du calendrier :
- photos utilisées : photos/<marque>/<dossier>/<sujet>-01.jpg, -02.jpg… (jpg, png ou webp),
  à côté du fichier indiqué dans la colonne « Photo / vidéo ». Elles sont prises dans l'ordre.
  Tant qu'il n'y en a aucune, un plan « PHOTO À FOURNIR » est créé pour chaque étape décrite
  dans le calendrier. Ajoutez les photos puis relancez le script.
- zoom lent alterné (avant / arrière) sur chaque photo, fondus enchaînés entre les plans ;
- titre d'accroche (colonne « Texte visuel ») dès la première image, pendant environ 2,5 s ;
- carte de fin aux couleurs de la marque avec l'appel à l'action ;
- piste audio silencieuse : la musique s'ajoute dans Instagram.

Sorties dans reels/<marque>/ : <date>-<sujet>.mp4, <date>-<sujet>.txt (légende + hashtags)
et <date>-<sujet>-couverture.jpg (image de couverture du réel).
"""
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generer_visuels import (CREME, EXT_PHOTO, OLIVE, OR, RACINE, ROUGE, STORY,  # noqa: E402
                             ajuster, espace, fond, lignes, texte, titre)

W, H = STORY
FPS = 30
FONDU = 0.8          # durée des fondus enchaînés (s)
FIN = 3.5            # durée de la carte de fin (s)
ACCROCHE = 2.6       # durée d'affichage du titre d'accroche (s)
ZOOM = 0.12          # amplitude du zoom lent (12 %)


def photos_reel(chemin_video):
    """Photos numérotées <sujet>-NN.* rangées à côté du fichier indiqué dans le calendrier."""
    p = RACINE / chemin_video
    if not p.parent.exists():
        return []
    res = [f for f in p.parent.iterdir()
           if f.suffix.lower() in EXT_PHOTO and re.fullmatch(re.escape(p.stem) + r"-\d+", f.stem)]
    return sorted(res)


def etapes(description):
    """'farine en fontaine, œufs, assiette finale (20-30 s)' -> ['farine en fontaine', 'œufs', 'assiette finale']"""
    d = re.sub(r"\([^)]*\)", "", description)
    res = [e.strip() for e in d.split(",") if e.strip()]
    if len(res) < 3:  # description sans étapes : au moins 4 plans pour garder du rythme
        res = [f"{d.strip()} ({k}/4)" for k in range(1, 5)]
    return res


def image_plan(photo, chemin_attendu, description, sortie):
    """Image 2160x3840 (2x) pour un zoom fluide sans tremblement."""
    if photo:
        img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
        img = ImageOps.fit(img, (W * 2, H * 2), method=Image.LANCZOS, centering=(0.5, 0.45))
    else:
        img, _ = fond(STORY, None, chemin_attendu, description)
        img = img.resize((W * 2, H * 2), Image.LANCZOS)
    img.save(sortie)


def calque_accroche(txt, sortie):
    """Carte crème dans le tiers haut (hors zones masquées par l'interface Instagram)."""
    img = Image.new("RGBA", STORY, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    p, ls = ajuster(d, txt, W - 280, 96, lignes_max=3)
    lh = p.size * 1.15
    x0, x1, y0 = 100, W - 100, 380
    y1 = y0 + 56 + 34 + 30 + lh * len(ls) + 46
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=CREME + (245,))
    d.rounded_rectangle([x0 + 14, y0 + 14, x1 - 14, y1 - 14], radius=22, outline=OR, width=2)
    espace(d, (x0, y0 + 52), "DA LAURA  ·  CANNES", texte(26, True), OLIVE, ecart=5, largeur=x1 - x0)
    y = y0 + 52 + 34 + 30
    for l in ls:
        d.text((W / 2, y), l, font=p, fill=ROUGE, anchor="ma")
        y += lh
    img.save(sortie)


def carte_fin(cta, sortie):
    img = Image.new("RGB", (W * 2, H * 2), CREME)
    d = ImageDraw.Draw(img)
    s = 2  # dessin en 2x
    d.rectangle([70 * s, 300 * s, (W - 70) * s, (H - 420) * s], outline=OR, width=3 * s)
    espace(d, (0, 560 * s), "RESTAURANT ITALIEN  ·  CANNES", texte(30 * s, True), OLIVE, ecart=6 * s, largeur=W * s)
    d.text((W * s / 2, 640 * s), "Da Laura", font=titre(150 * s), fill=ROUGE, anchor="ma")
    d.rectangle([(W / 2 - 60) * s, 860 * s, (W / 2 + 60) * s, 864 * s], fill=OR)
    y = 930 * s
    for l in lignes(d, cta, texte(46 * s), (W - 260) * s)[:4]:
        d.text((W * s / 2, y), l, font=texte(46 * s), fill=OLIVE, anchor="ma")
        y += 64 * s
    img.save(sortie)


def ffmpeg_reel(plans, durees, accroche_png, sortie):
    """plans : images 2x ; durees : durée de chaque plan (la dernière = carte de fin)."""
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for p in plans:
        args += ["-i", str(p)]
    args += ["-loop", "1", "-t", str(ACCROCHE + 0.2), "-i", str(accroche_png)]
    total = sum(durees) - FONDU * (len(durees) - 1)
    args += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]

    f = []
    for i, d in enumerate(durees):
        n = int(round(d * FPS))
        if i == len(durees) - 1:  # carte de fin : zoom très léger
            z = f"1+{0.03}*on/{n}"
        elif i % 2 == 0:          # zoom avant
            z = f"1+{ZOOM}*on/{n}"
        else:                     # zoom arrière
            z = f"1+{ZOOM}-{ZOOM}*on/{n}"
        f.append(f"[{i}:v]zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                 f":d={n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[p{i}]")
    cur, t = "[p0]", durees[0]
    for i in range(1, len(durees)):
        off = t - FONDU
        f.append(f"{cur}[p{i}]xfade=transition=fade:duration={FONDU}:offset={off:.3f}[x{i}]")
        cur, t = f"[x{i}]", off + durees[i]
    ia = len(plans)
    f.append(f"[{ia}:v]format=rgba,fade=t=out:st={ACCROCHE - 0.4}:d=0.4:alpha=1[acc]")
    f.append(f"{cur}[acc]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]")

    args += ["-filter_complex", ";".join(f), "-map", "[v]", "-map", f"{ia + 1}:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-level", "4.1",
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-shortest",
             "-movflags", "+faststart", str(sortie)]
    subprocess.run(args, check=True)
    return total


def main(csv_path):
    csv_path = Path(csv_path)
    marque = re.match(r"(.+)-\d{4}-\d{2}$", csv_path.stem).group(1)
    with open(csv_path if csv_path.is_absolute() else RACINE / csv_path, encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh, delimiter=";") if r["Format"] == "Réel"]

    dossier = RACINE / "reels" / marque
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = []
    for r in rows:
        j, mo, a = r["Date"].split("/")
        champ = re.sub(r"^À fournir\s*:\s*", "", r["Photo / vidéo"])
        chemin, _, desc = champ.partition(" — ")
        chemin = chemin.strip()
        sujet = Path(chemin).stem
        nom = f"{a}-{mo}-{j}-{sujet}"
        photos = photos_reel(chemin)
        base = str(Path(chemin).with_suffix(""))

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            plans = []
            if photos:
                for k, ph in enumerate(photos[:7]):
                    image_plan(ph, None, None, tmp / f"plan{k}.png")
                    plans.append(tmp / f"plan{k}.png")
            else:
                for k, e in enumerate(etapes(desc)[:7], 1):
                    image_plan(None, f"{base}-{k:02d}.jpg", f"Plan {k} : {e}", tmp / f"plan{k}.png")
                    plans.append(tmp / f"plan{k}.png")
            n = len(plans)
            # durée par plan pour rester entre 15 et 30 s, carte de fin comprise
            d = 5.0 if n <= 4 else 4.0
            while n * d + FIN - FONDU * n < 15:
                d += 0.5
            while n * d + FIN - FONDU * n > 28 and d > 2.5:
                d -= 0.5
            carte_fin(r["Appel à l'action"], tmp / "fin.png")
            calque_accroche(r["Texte visuel"], tmp / "accroche.png")
            total = ffmpeg_reel(plans + [tmp / "fin.png"], [d] * n + [FIN], tmp / "accroche.png",
                                dossier / f"{nom}.mp4")
            # couverture : premier plan + accroche
            couv = Image.open(plans[0]).resize(STORY, Image.LANCZOS).convert("RGBA")
            couv.alpha_composite(Image.open(tmp / "accroche.png"))
            couv.convert("RGB").save(dossier / f"{nom}-couverture.jpg", quality=95)

        (dossier / f"{nom}.txt").write_text(r["Légende"] + "\n\n" + r["Hashtags"] + "\n", encoding="utf-8")
        bilan.append((nom, total, n, bool(photos)))
        print(f"{nom}.mp4 : {total:.1f} s, {n} plans" + ("" if photos else " (photos à fournir)"))
    return bilan


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "calendriers/da-laura-2026-12.csv")
