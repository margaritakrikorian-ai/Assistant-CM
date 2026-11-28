"""Intro « flash » inspirée du modèle Canva « Nomade » choisi par l'utilisatrice : photos du restaurant qui défilent
très vite (une toutes les 0,5 s), grain de pellicule et image légèrement adoucie, nom du restaurant fixe au centre.

    python3 outils/intro_flash.py            → reels/da-laura/intro-flash/da-laura-intro.mp4 (avec texte)
                                               + da-laura-intro-fond.mp4 (sans texte, pour Canva)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

R = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
PHOTOS = [("facade-rue", .5), ("huile-burrata", .55), ("chef-citrons", .5), ("langoustines-pates", .45), ("salle-banquette-jaune", .5),
          ("poele-flambee", .55), ("tagliatelle-machine", .45), ("terrasse-fauteuils", .5), ("tiramisu-fraise", .5), ("rigatoni-mains-chef", .55)]
PAS = 0.5


def police(nom, t, poids=None):
    f = ImageFont.truetype(str(R / "outils/polices" / nom), t)
    if poids:
        f.set_variation_by_axes([poids])
    return f


def prepare(nom, cy):
    im = ImageOps.exif_transpose(Image.open(R / f"photos/da-laura/cannes/{nom}.jpg")).convert("RGB")
    im = appliquer_charte(ImageOps.fit(im, (int(W * 1.06), int(H * 1.06)), Image.LANCZOS, centering=(0.5, cy)))
    im = im.filter(ImageFilter.GaussianBlur(1.1))                      # image adoucie, comme le modèle
    im = ImageEnhance.Color(im).enhance(0.88)
    a = np.asarray(im).astype(np.float32)
    a = a * 0.86 + 14                                                   # noirs légèrement relevés (rendu pellicule)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def titre():
    cal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cal)
    f1, f2 = police("CormorantGaramond.ttf", 190, 700), police("Lato-Bold.ttf", 38)
    d.text((W / 2, 1010), "DA LAURA", font=f1, fill=(255, 255, 255, 255), anchor="ms")
    s, e = "RESTAURANT ITALIEN  ·  CANNES", 5
    lg = sum(d.textlength(c, font=f2) for c in s) + e * (len(s) - 1)
    x = (W - lg) / 2
    for c in s:
        d.text((x, 1085), c, font=f2, fill=(255, 255, 255, 255), anchor="ls")
        x += d.textlength(c, font=f2) + e
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre.putalpha(cal.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.45)))
    return Image.alpha_composite(ombre, cal)


def rendre(sortie, avec_texte):
    imgs = [prepare(n, cy) for n, cy in PHOTOS]
    t_cal = titre() if avec_texte else None
    rng = np.random.default_rng(3)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-c:v", "libx264", "-crf", "19",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(sortie)], stdin=subprocess.PIPE)
    n_img = int(PAS * FPS)
    for i, im in enumerate(imgs):
        for k in range(n_img):
            z = 1 + 0.03 * k / n_img                                    # léger zoom pendant chaque photo
            cw, ch = im.width / z, im.height / z
            fr = im.resize((W, H), Image.BILINEAR, box=((im.width - cw) / 2, (im.height - ch) / 2, (im.width + cw) / 2, (im.height + ch) / 2))
            a = np.asarray(fr).astype(np.int16)
            a += rng.normal(0, 9, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.int16)  # grain qui bouge
            fr = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
            if t_cal:
                fr = Image.alpha_composite(fr, t_cal)
            p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print(sortie.relative_to(R))


if __name__ == "__main__":
    out = R / "reels/da-laura/intro-flash"
    out.mkdir(parents=True, exist_ok=True)
    rendre(out / "da-laura-intro.mp4", True)
    rendre(out / "da-laura-intro-fond.mp4", False)
