"""Détoure un plat (rembg) dans une zone de la photo et garde uniquement le plus grand objet (le plat)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove, new_session
from scipy import ndimage

RACINE = Path(__file__).resolve().parents[2]
SESSION = None


def detourer(src, boite, sortie, ellipse=None):
    global SESSION
    SESSION = SESSION or new_session("isnet-general-use")
    im = ImageOps.exif_transpose(Image.open(RACINE / src)).convert("RGB")
    w, h = im.size
    im = im.crop((int(boite[0] * w), int(boite[1] * h), int(boite[2] * w), int(boite[3] * h)))
    rgba = remove(im, session=SESSION)
    a = np.asarray(rgba.getchannel("A")).astype(np.float32)
    if ellipse:  # assiette blanche sur nappe claire : on ajoute l'ellipse de l'assiette (fractions de la photo entière)
        cx, cy, rx, ry = ellipse[0] * w - boite[0] * w, ellipse[1] * h - boite[1] * h, ellipse[2] * w, ellipse[3] * h
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        a = np.maximum(a, np.clip((1 - e) * 255 / 0.02, 0, 255))
    lab, n = ndimage.label(a > 128)
    if n:
        tailles = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
        garde = lab == (1 + int(np.argmax(tailles)))
        garde = ndimage.binary_fill_holes(garde)
        a = np.where(ndimage.binary_dilation(garde, iterations=2), a, 0)
    a = np.clip((a - 30) * 255 / 200, 0, 255)
    rgba = im.convert("RGBA")  # couleurs d'origine de la photo, seul le masque vient du détourage
    rgba.putalpha(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    rgba = rgba.crop(rgba.getbbox())
    Path(sortie).parent.mkdir(parents=True, exist_ok=True)
    rgba.save(sortie)


if __name__ == "__main__":
    detourer(sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3],
             [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None)
