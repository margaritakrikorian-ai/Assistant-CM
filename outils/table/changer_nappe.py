"""Remplace la nappe en dentelle d'une photo par la table en bois de la vidéo de référence (IMG_1023),
sans toucher au reste : plat, verres, couverts, serviette gardent leurs pixels d'origine.
La texture du bois est prise sur la vidéo, mise en perspective et floutée comme la profondeur de champ de la photo.

    python3 outils/table/changer_nappe.py burrata
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parents[2]
BOIS = RACINE / "photos/da-laura/ambiance/table-bois-reference.png"

# Formes à garder (en pixels de la photo 1365x2048) : (type, coordonnées, flou du bord, opacité gardée)
PHOTOS = {
    "burrata": {
        "src": "photos/da-laura/plats/burrata-truffe-prosciutto.jpg",
        "garder": [
            ("detour", (792, 1242, 712, 458), 2, 1.0),        # assiette et burrata : contour détecté, limité à cette ellipse
            ("ellipse", (792, 1242, 702, 449), 2, 1.0),       # + l'assiette elle-même (le bord que la détection rate)
            ("rect", (74, 0, 356, 785), 6, 1.0),              # pot blanc (flou)
            ("rect", (0, 412, 74, 990), 3, 1.0),              # verre vert à gauche
            ("rect", (0, 970, 90, 1642), 3, 1.0),             # corbeille dorée
            ("rect", (0, 1490, 58, 1745), 3, 1.0),            # pied de la corbeille
            ("poly", [(0, 1726), (136, 1634), (142, 1668), (0, 1848)], 2, 1.0),  # couteau en bas à gauche
            ("rect", (0, 2004, 228, 2048), 2, 1.0),           # serviette en bas à gauche
            ("poly", [(622, 612), (800, 618), (1365, 655), (1365, 822), (680, 822), (640, 700)], 3, 1.0),  # serviette, fourchette, couteau
            ("ellipse", (1106, 190, 345, 240), 10, 1.0),      # assiette du fond (floue)
            ("rect", (338, 0, 628, 300), 14, 0.55),           # verre à pied flou : on garde ses reflets
            ("rect", (690, 0, 790, 130), 10, 0.6),            # verre vert du fond
        ],
        # perspective du plan de la table : coins haut-gauche, haut-droit, bas-droit, bas-gauche
        "plan": [(160, -80), (1205, -80), (1900, 2048), (-535, 2048)],
        "flou": [(0, 13), (520, 9), (820, 2), (1100, 0), (1750, 0), (2048, 3)],  # (y, rayon) profondeur de champ
        "ombre": (800, 1300, 735, 480),
    },
}


def texture_bois(w, h, graine=5):
    im = Image.open(BOIS).convert("RGB")
    zone = np.asarray(im.crop((270, 1540, 740, 2120))).astype(np.float32)
    rng = np.random.default_rng(graine)
    BW, BH, R = 180, 320, 70
    out = np.zeros((h + BH, w + BW, 3), np.float32)
    pds = np.zeros((h + BH, w + BW, 1), np.float32)
    rx = np.minimum(1, np.minimum(np.arange(BW + R) + 1, BW + R - np.arange(BW + R)) / R)
    ry = np.minimum(1, np.minimum(np.arange(BH + R) + 1, BH + R - np.arange(BH + R)) / R)
    m = (ry[:, None] * rx[None, :])[..., None]
    for y in range(0, h, BH):
        for x in range(0, w, BW):
            sy, sx = rng.integers(0, zone.shape[0] - BH - R), rng.integers(0, zone.shape[1] - BW - R)
            b = zone[sy:sy + BH + R, sx:sx + BW + R]
            if rng.random() < 0.5:
                b = b[::-1]
            hh, ww = min(BH + R, out.shape[0] - y), min(BW + R, out.shape[1] - x)
            out[y:y + hh, x:x + ww] += b[:hh, :ww] * m[:hh, :ww]
            pds[y:y + hh, x:x + ww] += m[:hh, :ww]
    out = out[R // 2:R // 2 + h, R // 2:R // 2 + w] / np.maximum(pds[R // 2:R // 2 + h, R // 2:R // 2 + w], 1e-3)
    flou = np.asarray(Image.fromarray(out.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(90))).astype(np.float32)
    out = out - flou + out.reshape(-1, 3).mean(0)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def coeffs(dst, src):
    """Coefficients PIL PERSPECTIVE : pour chaque pixel de sortie (dst), le point de la texture (src)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def masque(taille, formes, photo=None):
    total = np.zeros(taille[::-1], np.float32)
    for kind, c, flou, op in formes:
        m = Image.new("L", taille, 0)
        d = ImageDraw.Draw(m)
        if kind == "detour":
            from rembg import remove, new_session
            from scipy import ndimage
            r = np.asarray(remove(photo, session=new_session("isnet-general-use"), only_mask=True)) > 40
            cx, cy, rx, ry = c
            yy, xx = np.mgrid[0:taille[1], 0:taille[0]]
            r &= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
            lab, n = ndimage.label(r)
            if n:
                r = lab == 1 + int(np.argmax(ndimage.sum(r, lab, range(1, n + 1))))
            r = ndimage.binary_fill_holes(ndimage.binary_closing(r, iterations=6))
            m = Image.fromarray((r * 255).astype(np.uint8))
        elif kind == "ellipse":
            cx, cy, rx, ry = c
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        elif kind == "rect":
            d.rounded_rectangle(c, 18, fill=255)
        else:
            d.polygon(c, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(flou))
        total = np.maximum(total, np.asarray(m).astype(np.float32) / 255 * op)
    return total


def main(nom):
    cfg = PHOTOS[nom]
    photo = Image.open(RACINE / cfg["src"]).convert("RGB")
    W, H = photo.size
    tw, th = 1500, 2600
    bois = texture_bois(tw, th)
    bois = bois.transform((W, H), Image.PERSPECTIVE, coeffs(cfg["plan"], [(0, 0), (tw, 0), (tw, th), (0, th)]),
                          Image.BICUBIC)
    # lumière du jour de la photo : le bois est un peu éclairci pour rester dans l'ambiance
    b = np.asarray(bois).astype(np.float32) * 1.18 + 6
    # ombre douce de l'assiette sur le bois
    cx, cy, rx, ry = cfg["ombre"]
    o = Image.new("L", (W, H), 0)
    ImageDraw.Draw(o).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    o = np.asarray(o.filter(ImageFilter.GaussianBlur(45))).astype(np.float32) / 255
    b *= (1 - 0.45 * o)[..., None]
    bois = Image.fromarray(b.clip(0, 255).astype(np.uint8))
    # profondeur de champ : même flou que la photo selon la hauteur
    ys, rs = zip(*cfg["flou"])
    niveaux = sorted(set(int(round(r)) for r in rs))
    couches = {r: np.asarray(bois.filter(ImageFilter.GaussianBlur(r)) if r else bois).astype(np.float32) for r in niveaux}
    rayon = np.interp(np.arange(H), ys, rs)
    res = np.zeros((H, W, 3), np.float32)
    for y in range(H):
        r = rayon[y]
        lo = max([n for n in niveaux if n <= r], default=0)
        hi = min([n for n in niveaux if n >= r], default=lo)
        t = 0 if hi == lo else (r - lo) / (hi - lo)
        res[y] = couches[lo][y] * (1 - t) + couches[hi][y] * t
    garde = masque((W, H), cfg["garder"], photo)[..., None]
    out = np.asarray(photo).astype(np.float32) * garde + res * (1 - garde)
    sortie = RACINE / f"photos/da-laura/table-bois/{nom}.jpg"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(sortie, quality=95)
    print(sortie.relative_to(RACINE))


if __name__ == "__main__":
    main(sys.argv[1])
