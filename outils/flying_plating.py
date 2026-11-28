"""Flying plating : un plat qui flotte devant le décor de Da Laura Cannes (4:5, 1080x1350).

Usage :
  python3 outils/flying_plating.py photo_plat.jpg fond.jpg sortie.jpg [--masque masque.png]

- Détourage automatique du plat (rembg, modèle isnet-general-use). Si l'assiette n'est pas
  entièrement gardée, fournir --masque (PNG blanc = à garder, même taille que la photo).
- Fond flouté (effet objectif pro), assiette agrandie et légèrement penchée (-6°),
  ombre douce au sol, 5-6 feuilles/éléments du plat qui volent autour (bords nets uniquement,
  jamais de morceaux découpés en carré).
"""
import argparse
import cv2, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

W, H = 1080, 1350

def decouper(photo, masque=None):
    im = Image.open(photo).convert('RGB')
    if masque:
        m = np.array(Image.open(masque).convert('L'))
    else:
        from rembg import remove, new_session
        m = np.array(remove(im, session=new_session('isnet-general-use'), only_mask=True))
    rgba = Image.fromarray(np.dstack([np.array(im), m]))
    return rgba.crop(Image.fromarray(m).getbbox())

def elements(plat, n=6, seed=4):
    """Petits éléments pris sur le bord du plat (là où le fond est transparent)."""
    rng = np.random.default_rng(seed); a = np.array(plat.split()[3]); h, w = a.shape; out = []
    for _ in range(200):
        bw, bh = int(w * .18), int(h * .2)
        x, y = rng.integers(0, w - bw), rng.integers(0, h - bh)
        win = a[y:y + bh, x:x + bw]
        cov = (win > 170).mean()
        if 0.15 < cov < 0.45:   # un bout de feuille, pas un morceau plein
            p = plat.crop((x, y, x + bw, y + bh)); al = np.where(np.array(p.split()[3]) > 170, 255, 0).astype(np.uint8)
            al = cv2.erode(al, np.ones((3, 3)))
            e = np.zeros_like(al); cv2.ellipse(e, (bw // 2, bh // 2), (bw // 2 - 6, bh // 2 - 6), 0, 0, 360, 255, -1)
            p.putalpha(Image.fromarray(np.minimum(al, cv2.GaussianBlur(e, (0, 0), 5))).filter(ImageFilter.GaussianBlur(1)))
            out.append(p)
        if len(out) >= n: break
    return out

def composer(photo, fond, sortie, masque=None):
    plat = decouper(photo, masque)
    bg = Image.open(fond).convert('RGB')
    r = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * r) + 1, int(bg.height * r) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    cv_ = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(14))).enhance(.88).convert('RGBA')
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse([300, 1120, 800, 1230], fill=170)
    cv_.paste(Image.new('RGBA', (W, H), (20, 12, 8, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(35)))
    rng = np.random.default_rng(7)
    places = [(70, 170, 35, 1.5), (850, 260, -40, 0), (760, 120, 120, 0), (110, 560, -150, 0), (890, 640, 70, 2), (60, 860, 10, 2.5)]
    for p, (x, y, rot, bl) in zip(elements(plat), places):
        p = p.resize((int(p.width * .6), int(p.height * .6)), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC, expand=True)
        cv_.alpha_composite(p.filter(ImageFilter.GaussianBlur(bl)) if bl else p, (x, y))
    pw = 820; plat = plat.resize((pw, int(plat.height * pw / plat.width)), Image.LANCZOS).rotate(-6, resample=Image.BICUBIC, expand=True)
    cv_.alpha_composite(plat, ((W - plat.width) // 2, 330))
    cv_.convert('RGB').save(sortie, quality=95)

if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('photo'); a.add_argument('fond'); a.add_argument('sortie'); a.add_argument('--masque')
    v = a.parse_args(); composer(v.photo, v.fond, v.sortie, v.masque)
