"""Filtre photo « charte Da Laura » : le même rendu de couleur sur toutes les photos.

Rendu NATUREL, fidèle aux photos déjà publiées sur le compte (choix de l'utilisatrice, 24/11/2026 :
l'ancien filtre chaud et doré était « trop jaune ») :
- couleurs et balance des blancs d'origine conservées : AUCUN réchauffement, aucune teinte ajoutée ;
- contraste doux en S, très léger (un peu plus de relief) ;
- « vibrance » légère : seules les couleurs ternes sont un peu ravivées, les couleurs vives restent telles quelles ;
- aucune perte de netteté (pas de flou).

Utilisation :
    python3 outils/charte_photo.py photos/da-laura/plats/ravioli-truffe.jpg ...      # une ou plusieurs photos
    python3 outils/charte_photo.py photos/da-laura                                   # tout un dossier
Les copies filtrées sont rangées dans photos/<marque>/charte/<même chemin>, les originaux ne sont jamais modifiés.
Les générateurs (stories plats du jour) appliquent ce filtre automatiquement.

Dans le code :  from charte_photo import appliquer_charte ; img = appliquer_charte(img)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

RACINE = Path(__file__).resolve().parent.parent
EXT = {".jpg", ".jpeg", ".png", ".webp"}

# Réglages de la charte (modifier ici pour faire évoluer le rendu de TOUTES les photos)
CHARTE = {
    "contraste_s": 0.12,   # part de courbe en S (0 = aucune)
    "vibrance": 0.10,      # ravive les couleurs ternes sans toucher les couleurs déjà vives
}


def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-8
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-8), 0)
    return h, s, mx


def _rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    choix = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.zeros(h.shape + (3,))
    for k, (a, b, c) in enumerate(choix):
        m = i == k
        out[m, 0], out[m, 1], out[m, 2] = a[m], b[m], c[m]
    return out


def appliquer_charte(img, c=CHARTE):
    """Renvoie une copie de l'image (PIL, RGB) avec le rendu de couleur de la charte (naturel)."""
    x = np.asarray(img.convert("RGB"), dtype=np.float64) / 255.0
    s = x * x * (3 - 2 * x)
    x = (1 - c["contraste_s"]) * x + c["contraste_s"] * s
    h, sat, v = _hsv(np.clip(x, 0, 1))
    sat = np.clip(sat + c["vibrance"] * sat * (1 - sat), 0, 1)
    x = _rgb(h, sat, v)
    return Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8))


def creer_hald(chemin=RACINE / "outils" / "charte-da-laura-hald.png", niveau=8):
    """Recrée la table de couleurs (HALD CLUT) qui applique le même filtre aux vidéos (ffmpeg haldclut)."""
    n = niveau * niveau
    i = np.arange(n ** 3)
    r, g, b = i % n, (i // n) % n, i // (n * n)
    px = (np.stack([r, g, b], -1) * 255.0 / (n - 1) + 0.5).astype(np.uint8)
    taille = niveau ** 3
    appliquer_charte(Image.fromarray(px.reshape(taille, taille, 3))).save(chemin)


def exporter(chemins):
    fichiers = []
    for c in chemins:
        p = (RACINE / c) if not Path(c).is_absolute() else Path(c)
        fichiers += sorted(f for f in p.rglob("*") if f.suffix.lower() in EXT) if p.is_dir() else [p]
    n = 0
    for f in fichiers:
        rel = f.relative_to(RACINE)
        if "charte" in rel.parts:
            continue
        # photos/<marque>/<reste>  ->  photos/<marque>/charte/<reste>
        parts = rel.parts
        dest = RACINE.joinpath(*parts[:2], "charte", *parts[2:]).with_suffix(".jpg")
        dest.parent.mkdir(parents=True, exist_ok=True)
        appliquer_charte(ImageOps.exif_transpose(Image.open(f))).save(dest, quality=97, subsampling=0)
        print(dest.relative_to(RACINE))
        n += 1
    print(f"{n} photo(s) passée(s) à la charte Da Laura.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--hald"]:
        creer_hald(); print("Table de couleurs vidéo recréée."); sys.exit()
    exporter(sys.argv[1:] or ["photos/da-laura"])
