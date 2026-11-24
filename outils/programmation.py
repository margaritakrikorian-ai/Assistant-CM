"""Outils communs à la programmation des publications de Da Laura (@dalaura.cannes).

Calendrier de programmation : calendriers/dalaura-AAAA-MM.csv (séparateur « ; », UTF-8)
Colonnes : date ; heure ; format ; fichier ; légende ; statut
- date   : AAAA-MM-JJ          - heure : HH:MM (heure de Paris)
- format : post | story | reel  (un carrousel est un « post » avec plusieurs fichiers séparés par « + »)
- statut : à créer | validé client | programmé | publié
"""
import csv
import datetime
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageOps

RACINE = Path(__file__).resolve().parent.parent
PARIS = ZoneInfo("Europe/Paris")
COLONNES = ["date", "heure", "format", "fichier", "légende", "statut"]
STATUTS = ["à créer", "validé client", "programmé", "publié"]
FORMATS = {"post": (1080, 1350), "story": (1080, 1920), "reel": (1080, 1920)}

COMPTE = "@dalaura.cannes"
ADRESSE = "8 rue du 24 Août, Cannes"
TELEPHONE = "04 93 38 40 51"
BLOC_INFOS = f"Da Laura · {ADRESSE}\nRéservations : {TELEPHONE}"


# ---------- statut : comparaison stricte mais tolérante aux accents et majuscules ----------
def norm(txt):
    t = unicodedata.normalize("NFD", (txt or "").strip().lower())
    return re.sub(r"\s+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn"))


def est_valide_client(ligne):
    """Vrai UNIQUEMENT si le statut est exactement « validé client » (accents et majuscules ignorés)."""
    return norm(ligne.get("statut")) == "valide client"


# ---------- lecture / écriture du calendrier ----------
def fichiers_calendrier():
    return sorted((RACINE / "calendriers").glob("dalaura-[0-9][0-9][0-9][0-9]-[0-9][0-9].csv"))


def lire(chemin):
    with open(chemin, encoding="utf-8-sig", newline="") as fh:
        lignes = list(csv.DictReader(fh, delimiter=";"))
    for i, l in enumerate(lignes, 2):
        manquantes = [c for c in COLONNES if c not in l]
        if manquantes:
            raise SystemExit(f"{chemin.name} : colonnes manquantes {manquantes}")
        if norm(l["statut"]) not in [norm(s) for s in STATUTS]:
            raise SystemExit(f"{chemin.name}, ligne {i} : statut inconnu « {l['statut']} » (attendu : {', '.join(STATUTS)})")
        if l["format"].strip().lower() not in FORMATS:
            raise SystemExit(f"{chemin.name}, ligne {i} : format inconnu « {l['format']} » (post, story ou reel)")
    return lignes


def ecrire(chemin, lignes):
    tmp = chemin.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES, delimiter=";")
        w.writeheader()
        w.writerows({c: l.get(c, "") for c in COLONNES} for l in lignes)
    tmp.replace(chemin)


def moment(ligne):
    d = datetime.date.fromisoformat(ligne["date"].strip())
    h, m = (int(x) for x in ligne["heure"].strip().replace("h", ":").split(":")[:2])
    return datetime.datetime(d.year, d.month, d.day, h, m, tzinfo=PARIS)


def fichiers(ligne):
    return [RACINE / f.strip() for f in ligne["fichier"].split("+") if f.strip()]


# ---------- légende finale ----------
def legende_finale(ligne):
    """Légende + bloc adresse et réservations, inséré avant les hashtags."""
    texte = ligne["légende"].strip()
    if ligne["format"].strip().lower() == "story":
        return texte  # une story n'a pas de légende sur Instagram : texte de rappel uniquement
    parties = texte.rsplit("\n\n", 1)
    if len(parties) == 2 and parties[1].lstrip().startswith("#"):
        return f"{parties[0]}\n\n{BLOC_INFOS}\n\n{parties[1]}"
    return f"{texte}\n\n{BLOC_INFOS}"


# ---------- préparation des médias au bon format ----------
def preparer_image(src, dest, taille):
    """Copie l'image au format exact (JPEG). Si elle n'a pas déjà la bonne taille, elle est recadrée au centre."""
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if img.size != taille:
        img = ImageOps.fit(img, taille, Image.LANCZOS, centering=(0.5, 0.45))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=95, subsampling=0, optimize=True)
    return dest


def infos_video(src):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height,codec_name:format=duration", "-of", "default=nw=1", str(src)],
                             capture_output=True, text=True, timeout=60).stdout
    except FileNotFoundError:
        return {}
    return dict(l.split("=", 1) for l in out.split() if "=" in l)


def preparer_video(src, dest):
    """Copie le réel ; le réencode en MP4 H.264 1080x1920 si besoin (ffmpeg)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    i = infos_video(src)
    if i.get("width") == "1080" and i.get("height") == "1920" and i.get("codec_name") == "h264":
        shutil.copyfile(src, dest)
    else:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf",
                        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-c:a", "aac",
                        "-movflags", "+faststart", str(dest)], check=True)
    return dest


def problemes(ligne):
    """Liste des raisons qui empêchent de programmer ou publier ce contenu (vide = prêt)."""
    p = []
    fmt = ligne["format"].strip().lower()
    fs = fichiers(ligne)
    if not fs:
        p.append("aucun fichier indiqué")
    for f in fs:
        if not f.exists():
            p.append(f"fichier introuvable : {f.relative_to(RACINE)}")
    if fmt == "reel" and fs and fs[0].suffix.lower() not in (".mp4", ".mov"):
        p.append("un réel doit être une vidéo MP4")
    if fmt in ("post", "story") and any(f.suffix.lower() not in (".jpg", ".jpeg", ".png") for f in fs):
        p.append("un post ou une story doit être une image JPG ou PNG")
    if fmt == "story" and len(fs) > 1:
        p.append("une story = un seul fichier")
    if len(fs) > 10:
        p.append("un carrousel compte 10 images au maximum")
    if fmt != "story" and not ligne["légende"].strip():
        p.append("légende vide")
    if re.search(r"\[[^\]]+\]", ligne["légende"]):
        p.append("texte entre crochets à compléter dans la légende")
    for f in fs[:1]:
        if (f.parent / "PHOTO-A-FOURNIR.txt").exists() or f.with_suffix(".attente").exists():
            p.append("visuel provisoire (cadre « photo à fournir »)")
    return p
