"""Filtre photo « charte Da Laura » : le même rendu de couleur sur toutes les photos.

Le rendu, inspiré des photos du restaurant (terrasse au soleil, vichy, enseigne rouge et crème) :
- lumière chaude et dorée (balance des blancs réchauffée) ;
- noirs légèrement relevés et adoucis (aspect « film », jamais de noir bouché) ;
- hautes lumières teintées crème (#F1E6D3), ombres teintées brun chaud ;
- rouges, oranges et jaunes préservés (sauce tomate, fraises, vichy), verts et bleus atténués ;
- contraste doux en S, aucune perte de netteté (pas de flou).

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
    "chaleur": (1.035, 1.012, 0.91),           # multiplicateurs R, V, B
    "noir_releve": 0.045,                    # niveau du noir le plus profond (0 = noir pur)
    "blanc_max": 0.975,                      # niveau du blanc le plus clair
    "contraste_s": 0.30,                     # part de courbe en S (0 = aucune)
    "teinte_ombres": (0.035, 0.012, -0.020),  # ajout R, V, B dans les ombres (brun chaud)
    "teinte_lumieres": (0.010, 0.012, -0.030),  # ajout R, V, B dans les hautes lumières (crème)
    "saturation": 0.95,                      # saturation générale
    "verts_bleus": 0.72,                     # saturation des verts et des bleus
    "chauds": 1.06,                          # saturation des rouges, oranges et jaunes
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
    """Renvoie une copie de l'image (PIL, RGB) avec le rendu de couleur de la charte."""
    x = np.asarray(img.convert("RGB"), dtype=np.float64) / 255.0
    x = x * np.array(c["chaleur"])
    # courbe en S douce
    s = x * x * (3 - 2 * x)
    x = (1 - c["contraste_s"]) * x + c["contraste_s"] * np.clip(s, 0, 1)
    # saturation sélective
    h, sat, v = _hsv(np.clip(x, 0, 1))
    deg = h * 360
    chaud = (deg < 65) | (deg > 330)
    froid = (deg > 75) & (deg < 300)
    facteur = np.where(chaud, c["chauds"], np.where(froid, c["verts_bleus"], 1.0)) * c["saturation"]
    x = _rgb(h, np.clip(sat * facteur, 0, 1), v)
    # virage partiel : ombres brun chaud, lumières crème
    lum = (0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2])[..., None]
    x = x + (1 - lum) ** 2 * np.array(c["teinte_ombres"]) + lum ** 2 * np.array(c["teinte_lumieres"])
    # noirs relevés et blancs adoucis
    x = c["noir_releve"] + (c["blanc_max"] - c["noir_releve"]) * np.clip(x, 0, 1)
    return Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8))


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
    exporter(sys.argv[1:] or ["photos/da-laura"])
