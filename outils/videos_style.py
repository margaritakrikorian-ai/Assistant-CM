"""Vidéos courtes dans le style préféré de l'utilisatrice (docs/style-video-prefere.md) :
une idée par vidéo, mouvement lent, typographie éditoriale minimaliste. MP4 1080x1920, 30 i/s, piste son muette
(la musique s'ajoute dans Instagram).

    python3 outils/videos_style.py [dolce|stop-motion|fatto-a-mano|tout]

Ne jamais recopier les formats des vidéos de référence : en reprendre l'esprit avec de nouveaux procédés.
"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

R = Path(__file__).resolve().parent.parent
POL = R / "outils/polices"
OUT = R / "reels/da-laura/propositions-style"
W, H, FPS = 1080, 1920, 30
BLANC = (255, 252, 246)
CREME = (244, 237, 225)
OR = (236, 214, 160)


def police(nom, t, poids=None):
    f = ImageFont.truetype(str(POL / nom), t)
    if poids:
        f.set_variation_by_axes([poids])
    return f


def photo(nom, maxi=2400):
    im = ImageOps.exif_transpose(Image.open(R / f"photos/da-laura/cannes/{nom}.jpg")).convert("RGB")
    im.thumbnail((maxi, maxi), Image.LANCZOS)
    return appliquer_charte(im)


def lisse(x):
    x = min(1, max(0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def cadrage(im, cx, cy, z, w, h):
    """Recadre im autour de (cx, cy) (0-1) au zoom z pour remplir w x h."""
    iw, ih = im.size
    base = max(w / iw, h / ih)
    cw, ch = w / (base * z), h / (base * z)
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return im.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def texte_espace(d, xy, txt, f, fill, ecart, ancre="l"):
    larg = sum(d.textlength(c, font=f) for c in txt) + ecart * (len(txt) - 1)
    x, y = xy
    if ancre == "m":
        x -= larg / 2
    elif ancre == "r":
        x -= larg
    for c in txt:
        d.text((x, y), c, font=f, fill=fill, anchor="ls")
        x += d.textlength(c, font=f) + ecart


def calque_texte(dessin):
    """Dessine sur un calque RGBA puis ajoute une ombre douce pour la lisibilité."""
    cal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dessin(ImageDraw.Draw(cal))
    a = cal.split()[3]
    ombre = Image.new("RGBA", (W, H), (10, 6, 4, 0))
    ombre.putalpha(a.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.55)))
    return Image.alpha_composite(ombre, cal)


class Video:
    def __init__(self, nom):
        self.sortie = OUT / f"{nom}.mp4"
        OUT.mkdir(parents=True, exist_ok=True)
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                                   "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                                   "-profile:v", "high", "-c:a", "aac", "-b:a", "128k", "-shortest",
                                   "-movflags", "+faststart", str(self.sortie)], stdin=subprocess.PIPE)

    def image(self, img):
        self.p.stdin.write(img.convert("RGB").tobytes())

    def fin(self):
        self.p.stdin.close()
        self.p.wait()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.5", "-i", str(self.sortie), "-frames:v", "1", "-q:v", "2",
                        str(self.sortie.with_name(self.sortie.stem + "-couverture.jpg"))], check=True)
        print(self.sortie.relative_to(R))


# 1. Écran partagé : macro en haut, plat entier en bas, viseur de mise au point
PLATS = [("langoustines-pates", "Pasta", (0.40, 0.42), (0.40, 0.45), 0.5),
         ("huile-burrata", "Burrata", (0.45, 0.70), (0.42, 0.50), 0.80),
         ("tiramisu-fraise", "Tiramisù", (0.52, 0.50), (0.52, 0.52), 0.5)]


def ecran_partage():
    v = Video("1-ecran-partage-plats")
    hh = H // 2
    f_nom, f_sig, f_phr = police("Lato-Regular.ttf", 34), police("Lato-Bold.ttf", 66), police("Lato-Regular.ttf", 38)
    duree = 4.3
    for i, (nom, label, macro, viseur, bas) in enumerate(PLATS):
        im = photo(nom)
        im_macro = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
        n = int(duree * FPS)
        for k in range(n):
            t = k / FPS
            p = t / duree
            img = Image.new("RGB", (W, H))
            img.paste(cadrage(im_macro, macro[0], macro[1] + 0.02 * p, 2.3 + 0.35 * p, W, hh), (0, 0))
            img.paste(cadrage(im, 0.5, bas, 1.0 + 0.06 * p, W, H - hh), (0, hh))
            img = img.convert("RGBA")

            def dessin(d):
                d.text((W - 60, 110), label, font=f_nom, fill=BLANC, anchor="rs")
                d.text((62, hh - 150), "Da Laura", font=f_sig, fill=BLANC, anchor="ls")
                d.text((62, hh - 88), "Cannes", font=f_sig, fill=BLANC, anchor="ls")
                for j, l in enumerate(["Le régime commence demain.", "Aujourd'hui, on se régale."]):
                    d.text((W - 60, H - 150 + j * 50), l, font=f_phr, fill=BLANC, anchor="rs")
                # viseur : 4 coins qui se resserrent sur le détail
                a = lisse((t - 0.5) / 0.6)
                if a > 0:
                    cx, cy = viseur[0] * W, hh + viseur[1] * (H - hh)
                    r = 150 + 90 * (1 - a)
                    c = 34
                    col = OR + (int(230 * a),)
                    for sx in (-1, 1):
                        for sy in (-1, 1):
                            x, y = cx + sx * r, cy + sy * r
                            d.line([(x, y), (x - sx * c, y)], fill=col, width=4)
                            d.line([(x, y), (x, y - sy * c)], fill=col, width=4)
                    d.line([(cx - 10, cy), (cx + 10, cy)], fill=col, width=2)
                    d.line([(cx, cy - 10), (cx, cy + 10)], fill=col, width=2)
            img = Image.alpha_composite(img, calque_texte(dessin))
            v.image(img)
    v.fin()


# 2. Travelling lent dans la rue + titre qui s'écrit
def coin_italie():
    v = Video("2-un-coin-d-italie")
    im = ImageEnhance.Brightness(photo("facade-passants", 3000)).enhance(0.9)
    ih = H
    iw = int(im.width * H / im.height)
    grand = im.resize((iw, ih), Image.LANCZOS)
    f_t, f_s = police("PlayfairDisplay-Italic.ttf", 118), police("Lato-Bold.ttf", 32)
    titre, sous = "Un coin d'Italie", "AU CŒUR DE CANNES"
    duree = 7.5
    d0 = ImageDraw.Draw(grand)
    larg = d0.textlength(titre, font=f_t)
    x0, y = (W - larg) / 2, 930
    for k in range(int(duree * FPS)):
        t = k / FPS
        x = (iw - W) * (0.15 + 0.55 * lisse(t / duree))
        img = grand.crop((int(x), 0, int(x) + W, H)).convert("RGBA")
        voile = Image.new("RGBA", (W, H), (12, 8, 6, 0))
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse([-200, y - 300, W + 200, y + 260], fill=120)
        voile.putalpha(g.filter(ImageFilter.GaussianBlur(110)))
        img = Image.alpha_composite(img, voile)
        reveal = (t - 1.0) / 1.8  # l'écriture avance de gauche à droite

        def dessin(d):
            if reveal > 0:
                d.text((x0, y), titre, font=f_t, fill=BLANC, anchor="ls")
            a = lisse((t - 3.0) / 0.8)
            if a > 0:
                texte_espace(d, (W / 2, y + 95), sous, f_s, CREME + (int(255 * a),), 9, "m")
        cal = calque_texte(dessin)
        if 0 < reveal < 1:
            m = Image.new("L", (W, H), 255)
            xm = x0 + larg * reveal
            ImageDraw.Draw(m).rectangle([xm, y - 150, W, y + 60], fill=0)
            a = cal.split()[3]
            cal.putalpha(Image.composite(a, Image.new("L", (W, H), 0), m.filter(ImageFilter.GaussianBlur(6))))
        img = Image.alpha_composite(img, cal)
        v.image(img)
    v.fin()


# 3. Grande serif éditoriale sur fond sombre : la flamme
def cucina_autentica():
    v = Video("3-cucina-autentica")
    im = ImageEnhance.Brightness(photo("poele-flambee")).enhance(0.82)
    f_t = police("CormorantGaramond.ttf", 176, 400)
    f_s, f_b = police("Lato-Bold.ttf", 30), police("Lato-Regular.ttf", 32)
    duree = 8.0
    for k in range(int(duree * FPS)):
        t = k / FPS
        img = cadrage(im, 0.5, 0.58, 1.0 + 0.08 * (t / duree), W, H).convert("RGBA")
        grad = Image.new("L", (1, H))
        for yy in range(H):
            grad.putpixel((0, yy), int(215 * max(0, 1 - yy / 900) ** 1.4))
        noir = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        noir.putalpha(grad.resize((W, H)))
        img = Image.alpha_composite(img, noir)

        def dessin(d):
            for j, (mot, t0) in enumerate([("Cucina", 0.6), ("Autentica", 1.3)]):
                a = lisse((t - t0) / 0.9)
                if a > 0:
                    d.text((W / 2, 360 + j * 165 + 20 * (1 - a)), mot, font=f_t, fill=BLANC + (int(255 * a),), anchor="ms")
            a = lisse((t - 2.4) / 0.8)
            if a > 0:
                texte_espace(d, (W / 2, 640), "DAL 1992", f_s, CREME + (int(255 * a),), 10, "m")
                d.text((W / 2, H - 120), "Da Laura Cannes", font=f_b, fill=CREME + (int(230 * a),), anchor="ms")
        img = Image.alpha_composite(img, calque_texte(dessin))
        v.image(img)
    v.fin()


# ---- Nouveaux procédés (28/11/2026) : même esprit que les références, jamais les mêmes formats ----
BORDEAUX = (122, 31, 43)
CREME_BG = (244, 237, 225)


def dolce():
    """Texte derrière le dessert détouré, sur fond crème de la charte."""
    from rembg import remove, new_session
    v = Video("4-dolce-texte-derriere")
    im = ImageOps.exif_transpose(Image.open(R / "photos/da-laura/cannes/tiramisu-fraise.jpg")).convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)
    dec = remove(appliquer_charte(im), session=new_session("isnet-general-use"))
    dec = dec.crop(dec.split()[3].point(lambda a: 255 if a > 60 else 0).getbbox())
    lw = 720
    dec = dec.resize((lw, int(dec.height * lw / dec.width)), Image.LANCZOS)
    fond = Image.new("RGB", (W, H), CREME_BG)
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).ellipse([-300, -200, W + 300, H + 200], fill=255)
    fond = Image.composite(fond, Image.new("RGB", (W, H), (226, 214, 196)), vg.filter(ImageFilter.GaussianBlur(260)))
    f_t = police("CormorantGaramond.ttf", 330, 400)
    f_s, f_b = police("Lato-Regular.ttf", 34), police("Lato-Bold.ttf", 26)
    mot = "Dolce"
    d0 = ImageDraw.Draw(fond)
    larg = [d0.textlength(c, font=f_t) for c in mot]
    x0, yt = (W - sum(larg)) / 2, 780
    duree = 7.0
    for k in range(int(duree * FPS)):
        t = k / FPS
        img = fond.copy().convert("RGBA")
        cal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(cal)
        x = x0
        for i, c in enumerate(mot):  # les lettres montent une à une derrière le verre
            a = lisse((t - 0.4 - i * 0.18) / 0.8)
            if a > 0:
                d.text((x, yt + 60 * (1 - a)), c, font=f_t, fill=BORDEAUX + (int(255 * a),), anchor="ls")
            x += larg[i]
        img = Image.alpha_composite(img, cal)
        z = 0.94 + 0.08 * lisse(t / duree)
        g = dec.resize((int(dec.width * z), int(dec.height * z)), Image.BICUBIC)
        gx, gy = (W - g.width) // 2, int(yt - 85 - 20 * lisse(t / duree))
        ombre = Image.new("L", (W, H), 0)
        ImageDraw.Draw(ombre).ellipse([gx + 60, gy + g.height - 40, gx + g.width - 60, gy + g.height + 50], fill=120)
        o = Image.new("RGBA", (W, H), (60, 40, 30, 0))
        o.putalpha(ombre.filter(ImageFilter.GaussianBlur(35)))
        img = Image.alpha_composite(img, o)
        img.alpha_composite(g, (gx, gy))
        a = lisse((t - 2.6) / 0.8)
        if a > 0:
            d2 = ImageDraw.Draw(img)
            d2.text((W / 2, H - 150), "Tiramisù aux fraises", font=f_s, fill=BORDEAUX + (int(255 * a),), anchor="ms")
            texte_espace(d2, (W / 2, H - 95), "DA LAURA  ·  CANNES", f_b, BORDEAUX + (int(200 * a),), 8, "m")
        v.image(img)
    v.fin()


def stop_motion():
    """Les 4 photos du dressage enchaînées image par image : le geste du chef prend vie."""
    v = Video("5-stop-motion-dernier-geste")
    ims = [photo(f"chef-dressage-{i}") for i in range(1, 5)]
    seq = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3]
    f_t, f_b = police("CormorantGaramond-Italic.ttf", 92, 500), police("Lato-Bold.ttf", 26)
    pas = 0.32
    for k in range(int(len(seq) * pas * FPS)):
        v.image(cadrage(ims[seq[int(k / FPS / pas)]], 0.55, 0.45, 1.12, W, H))
    tenue = 3.0
    for k in range(int(tenue * FPS)):
        t = k / FPS
        img = cadrage(ims[3], 0.58, 0.55, 1.12 + 0.18 * lisse(t / tenue), W, H).convert("RGBA")

        def dessin(d):
            a = lisse((t - 0.5) / 0.8)
            if a > 0:
                d.text((W / 2, 300), "Le dernier geste.", font=f_t, fill=BLANC + (int(255 * a),), anchor="ms")
                texte_espace(d, (W / 2, H - 140), "DA LAURA  ·  CANNES", f_b, BLANC + (int(220 * a),), 8, "m")
        v.image(Image.alpha_composite(img, calque_texte(dessin)))
    v.fin()


MAINS = [("rigatoni-main", 0.72, 0.38), ("gnocchi-roules", 0.30, 0.75), ("tagliatelle-machine", 0.45, 0.42),
         ("chef-couteau-poele", 0.50, 0.33), ("chef-citrons", 0.50, 0.58), ("rigatoni-mains-chef", 0.50, 0.58)]


def fatto_a_mano():
    """Coupes rythmées sur les mains, toujours au même endroit de l'image (raccord), puis on recule."""
    v = Video("6-fatto-a-mano")
    ims = [(photo(n), cx, cy) for n, cx, cy in MAINS]
    f_t, f_b = police("PlayfairDisplay-Italic.ttf", 104), police("Lato-Bold.ttf", 28)
    pas = 0.45
    for i, (im, cx, cy) in enumerate(ims[:-1]):
        for k in range(int(pas * FPS)):
            v.image(cadrage(im, cx, cy, 1.9 + 0.12 * k / (pas * FPS), W, H))
    im, cx, cy = ims[-1]
    tenue = 3.2
    for k in range(int(tenue * FPS)):
        t = k / FPS
        z = 1.9 - 0.85 * lisse(t / 1.6)
        img = cadrage(im, cx, cy - 0.08 * lisse(t / 1.6), z, W, H).convert("RGBA")

        a = lisse((t - 1.2) / 0.8)
        if a > 0:  # écriture bordeaux sur la veste blanche du chef
            cal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(cal)
            d.text((W / 2, 330), "Fatto a mano", font=f_t, fill=BORDEAUX + (int(255 * a),), anchor="ms")
            texte_espace(d, (W / 2, 400), "CHAQUE JOUR, CHEZ DA LAURA", f_b, BORDEAUX + (int(230 * a),), 7, "m")
            img = Image.alpha_composite(img, cal)
        v.image(img)
    v.fin()


if __name__ == "__main__":
    quoi = sys.argv[1] if len(sys.argv) > 1 else "tout"
    for nom, fn in [("dolce", dolce), ("stop-motion", stop_motion), ("fatto-a-mano", fatto_a_mano)]:
        if quoi in (nom, "tout"):
            fn()
