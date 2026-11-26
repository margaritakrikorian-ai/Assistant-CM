"""Réels « montage pro » (MP4 1080x1920, 30 i/s) : photos flottantes, transitions fluides, textes animés.

Utilisation :
    python3 outils/monter_reel_pro.py outils/reels/pro-<sujet>.json [--tiktok]

Scènes possibles (clé "type") :
- "plein"    : la photo en plein écran, mouvement lent et adouci (zoom avant/arrière, glissement, montée) ;
- "flottant" : la photo en carte (bord crème, ombre portée) qui flotte et tourne légèrement
               au-dessus d'un fond tiré de la même photo, adouci et assombri ;
- "duo"      : deux cartes qui arrivent de chaque côté et flottent ensemble.
Transitions (clé "transition", au début de la scène) : "glisse" (filé horizontal avec flou de mouvement),
"zoom" (poussée avant avec flou radial léger), "fondu" (fondu enchaîné avec éclat de lumière).
Les textes (écriture craie de la charte) montent et apparaissent en fondu, calés sur des scènes.
La charte photo Da Laura (filtre naturel validé) est appliquée à chaque photo. Piste audio silencieuse :
la musique s'ajoute dans Instagram ou TikTok.
"""
import copy
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402
from monter_reel import calque_texte, carte_fin  # noqa: E402
from plats_du_jour import CREME  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
TR = 0.36  # durée d'une transition (s)


def doux(p):
    p = min(1.0, max(0.0, p))
    return 0.5 - 0.5 * math.cos(math.pi * p)


def charger(src, taille, centre=(0.5, 0.45)):
    im = ImageOps.exif_transpose(Image.open(RACINE / src)).convert("RGB")
    im = ImageOps.fit(im, taille, Image.LANCZOS, centering=centre)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    return appliquer_charte(im)


# ---------- scènes ----------
class Plein:
    def __init__(self, s):
        self.d, self.m, self.a = s["duree"], s.get("mouvement", "zoom-avant"), s.get("ampleur", 0.14)
        self.img = charger(s["source"], (int(W * 1.3), int(H * 1.3)), tuple(s.get("centre", [0.5, 0.45])))

    def image(self, t):
        p = doux(t / self.d) * 0.85 + 0.15 * (t / self.d)  # mouvement continu, adouci
        iw, ih = self.img.size
        z = {"zoom-avant": 1 + self.a * p, "zoom-arriere": 1 + self.a * (1 - p)}.get(self.m, 1 + self.a)
        cw, ch = iw / 1.3 / z, ih / 1.3 / z
        cx, cy = iw / 2, ih / 2
        mx, my = (iw - cw) / 2 * 0.9, (ih - ch) / 2 * 0.9
        if self.m == "gauche-droite":
            cx = iw / 2 - mx + 2 * mx * p
        elif self.m == "droite-gauche":
            cx = iw / 2 + mx - 2 * mx * p
        elif self.m == "monte":
            cy = ih / 2 + my - 2 * my * p
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        return self.img.resize((W, H), Image.BICUBIC, box=box)


def carte(src, largeur, centre=(0.5, 0.5), ratio=1.25):
    """Photo en carte : bord crème fin, coins arrondis, ombre portée douce (RGBA)."""
    h = int(largeur * ratio)
    ph = charger(src, (largeur, h), centre)
    b = 16
    c = Image.new("RGB", (largeur + 2 * b, h + 2 * b), CREME)
    c.paste(ph, (b, b))
    masque = Image.new("L", c.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle([0, 0, c.size[0] - 1, c.size[1] - 1], 22, fill=255)
    m = 70
    out = Image.new("RGBA", (c.size[0] + 2 * m, c.size[1] + 2 * m), (0, 0, 0, 0))
    ombre = Image.new("L", out.size, 0)
    ombre.paste(masque, (m, m + 26))
    ombre = ombre.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.6))
    out.putalpha(ombre)
    rgba = c.convert("RGBA")
    rgba.putalpha(masque)
    out.alpha_composite(rgba, (m, m))
    return out


def fond(src, centre=(0.5, 0.45)):
    im = charger(src, (int(W * 1.12), int(H * 1.12)), centre)
    im = im.resize((im.width // 8, im.height // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    im = im.resize((int(W * 1.12), int(H * 1.12)), Image.BICUBIC)
    return ImageEnhance.Brightness(im).enhance(0.62)


class Flottant:
    def __init__(self, s):
        self.d = s["duree"]
        self.fond = fond(s["source"], tuple(s.get("centre", [0.5, 0.45])))
        self.carte = carte(s["source"], s.get("largeur", 900), tuple(s.get("centre", [0.5, 0.5])), s.get("ratio", 1.25))
        self.y = s.get("y", 0.56)
        self.sens = s.get("sens", 1)

    def image(self, t):
        p = t / self.d
        bw, bh = self.fond.size
        z = 1 + 0.06 * doux(p)
        cw, ch = bw / 1.12 / z, bh / 1.12 / z
        img = self.fond.resize((W, H), Image.BICUBIC, box=((bw - cw) / 2, (bh - ch) / 2, (bw + cw) / 2, (bh + ch) / 2))
        img = img.convert("RGBA")
        entree = doux(t / 0.55)
        s = 0.9 + 0.1 * entree + 0.03 * p
        ang = self.sens * (2.2 * (1 - entree) + 1.4 * math.sin(2 * math.pi * t / 3.2))
        dy = 14 * math.sin(2 * math.pi * t / 2.6) + 60 * (1 - entree)
        c = self.carte.resize((int(self.carte.width * s), int(self.carte.height * s)), Image.BICUBIC)
        c = c.rotate(ang, Image.BICUBIC, expand=True)
        img.alpha_composite(c, (int(W / 2 - c.width / 2), int(H * self.y - c.height / 2 + dy)))
        return img.convert("RGB")


class Duo:
    def __init__(self, s):
        self.d = s["duree"]
        a, b = s["sources"]
        self.fond = fond(a)
        self.c1 = carte(a, 600, ratio=1.25)
        self.c2 = carte(b, 600, ratio=1.25)

    def image(self, t):
        img = self.fond.resize((W, H), Image.BICUBIC, box=(60, 100, 60 + W, 100 + H)).convert("RGBA")
        e1, e2 = doux(t / 0.5), doux((t - 0.18) / 0.5)
        for c, e, x0, y0, ang, ph in ((self.c1, e1, 330, 760, -4, 0), (self.c2, e2, 750, 1260, 3.5, 1.3)):
            r = c.rotate(ang + 1.2 * math.sin(2 * math.pi * (t + ph) / 3), Image.BICUBIC, expand=True)
            x = x0 + (-1 if x0 < 540 else 1) * 700 * (1 - e)
            y = y0 + 12 * math.sin(2 * math.pi * (t + ph) / 2.4)
            img.alpha_composite(r, (int(x - r.width / 2), int(y - r.height / 2)))
        return img.convert("RGB")


SCENES = {"plein": Plein, "flottant": Flottant, "duo": Duo}


# ---------- transitions ----------
def flou_h(im, force):
    if force < 0.02:
        return im
    k = max(1, int(W / (1 + 60 * force)))
    return im.resize((k, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def transition(kind, a, b, p):
    """a = image sortante, b = image entrante, p de 0 à 1."""
    e = doux(p)
    if kind == "glisse":
        f = math.sin(math.pi * p)  # flou maximal au milieu
        a, b = flou_h(a, f), flou_h(b, f)
        off = int(W * e)
        out = Image.new("RGB", (W, H))
        out.paste(a, (-off, 0))
        out.paste(b, (W - off, 0))
        return out
    if kind == "zoom":
        za, zb = 1 + 0.25 * e, 1.18 - 0.18 * e
        def z(im, k):
            cw, ch = W / k, H / k
            return im.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        f = math.sin(math.pi * p)
        out = Image.blend(z(a, za), z(b, zb), e)
        if f > 0.05:
            out = Image.blend(out, out.filter(ImageFilter.GaussianBlur(10 * f)), 0.6 * f)
        return out
    out = Image.blend(a, b, e)  # fondu avec éclat
    eclat = math.sin(math.pi * p) * 0.22
    return Image.blend(out, Image.new("RGB", (W, H), (255, 244, 226)), eclat)


# ---------- textes ----------
def preparer_textes(plan, bornes, tmp):
    tx = []
    for k, t in enumerate(plan.get("textes", [])):
        png = tmp / f"t{k}.png"
        calque_texte(t, png)
        a = bornes[t["scenes"][0]][0] + 0.12
        b = bornes[t["scenes"][1]][1] - 0.1
        tx.append((Image.open(png).convert("RGBA"), a, b))
    return tx


def poser_textes(img, textes, t):
    img = img.convert("RGBA")
    for calque, a, b in textes:
        if not (a <= t <= b):
            continue
        e = doux((t - a) / 0.4)
        s = 1 - doux((t - (b - 0.25)) / 0.25)
        alpha = e * s
        if alpha <= 0.01:
            continue
        c = calque if alpha > 0.99 else Image.fromarray(
            (np.asarray(calque) * np.array([1, 1, 1, alpha])).astype(np.uint8), "RGBA")
        img.alpha_composite(c, (0, int(46 * (1 - e))))
    return img.convert("RGB")


# ---------- montage ----------
def version_tiktok(plan):
    t = copy.deepcopy(plan)
    t["sortie"] = plan["sortie"].replace(".mp4", "-tiktok.mp4")
    for s in t["scenes"]:
        s["duree"] = max(1.0, round(s["duree"] * 0.7, 2))
    for k, tx in enumerate(t.get("textes", [])):
        tx["taille"] = tx.get("taille", 120) + 12
        if k == 0 and plan.get("accroche_tiktok"):
            tx["texte"] = plan["accroche_tiktok"]
            tx.pop("surtitre", None)
    t["fin"]["duree"] = 2.0
    t["fin"]["appel"] = plan["fin"].get("appel_tiktok", "On t'attend !")
    t["legende"] = plan.get("legende_tiktok", plan["legende"])
    t["hashtags"] = plan.get("hashtags_tiktok", plan["hashtags"])
    return t


def main(fichier, tiktok=False):
    plan = json.loads(Path(fichier).read_text(encoding="utf-8"))
    if tiktok:
        plan = version_tiktok(plan)
    sortie = RACINE / plan["sortie"]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    scenes = [SCENES[s["type"]](s) for s in plan["scenes"]]
    bornes, t0 = [], 0.0
    for s in scenes:
        bornes.append((t0, t0 + s.d))
        t0 += s.d
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        textes = preparer_textes(plan, bornes, tmp)
        carte_fin(plan["fin"], tmp / "fin.png")
        fin_img = Image.open(tmp / "fin.png").convert("RGB")
        dfin = plan["fin"].get("duree", 2.6)
        total = t0 + dfin
        n = int(round(total * FPS))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
             "-level", "4.1", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(sortie)],
            stdin=subprocess.PIPE)
        trans = [None] + [plan["scenes"][i].get("transition", "glisse") for i in range(1, len(scenes))]
        trans.append("fondu")  # vers la carte de fin

        def scene_img(i, t):
            if i == len(scenes):
                zf = 1 + 0.03 * min(1, max(0, (t - t0) / dfin))
                cw, ch = W / zf, H / zf
                return fin_img.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
            return poser_textes(scenes[i].image(t - bornes[i][0]), textes, t)

        limites = [b[1] for b in bornes]
        for f in range(n):
            t = f / FPS
            i = next((k for k, b in enumerate(bornes) if t < b[1]), len(scenes))
            img = None
            for k, lim in enumerate(limites):  # transition autour de chaque limite entre scènes
                if abs(t - lim) < TR / 2:
                    p = (t - (lim - TR / 2)) / TR
                    img = transition(trans[k + 1], scene_img(k, t), scene_img(k + 1, t), p)
                    break
            if img is None:
                img = scene_img(i, t)
            proc.stdin.write(img.tobytes())
        proc.stdin.close()
        proc.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.9", "-i", str(sortie), "-frames:v", "1", "-q:v", "2",
                    str(sortie.with_name(sortie.stem + "-couverture.jpg"))], check=True)
    sortie.with_suffix(".txt").write_text(plan["legende"].strip() + "\n\n" + plan["hashtags"] + "\n", encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} : {total:.1f} s, {len(scenes)} scènes + carte de fin")


if __name__ == "__main__":
    main(sys.argv[1], tiktok="--tiktok" in sys.argv[2:])
