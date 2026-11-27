"""Story animée « Piatti del giorno » : fond flou léger, titre qui s'écrit lettre par lettre, avec un clic de machine
à écrire pour chaque lettre (son créé ici, aucun son sous droits). MP4 1080x1920, 30 i/s, environ 6 s.

    python3 outils/story_anime.py <photo> <style: dalaura|classique> <sortie.mp4>
"""
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

R = Path(__file__).resolve().parent.parent
POL = R / "outils/polices"
W, H, FPS = 1080, 1920, 30
CREME = (244, 237, 225)
SR = 44100


def police(nom, t, poids=None):
    f = ImageFont.truetype(str(POL / nom), t)
    if poids:
        f.set_variation_by_axes([poids])
    return f


def fond(photo, centre=(0.5, 0.5), zoom=0.62):
    im = ImageOps.exif_transpose(Image.open(R / photo)).convert("RGB")
    w, h = im.size
    cw, ch = w * zoom, h * zoom
    cx, cy = w * centre[0], h * centre[1]
    im = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2)))
    im = appliquer_charte(ImageOps.fit(im, (int(W * 1.06), int(H * 1.06)), Image.LANCZOS))
    im = im.filter(ImageFilter.GaussianBlur(3.5))  # flou léger : on devine encore bien le détail
    return ImageEnhance.Brightness(im).enhance(0.8)


def clic(graine):
    """Un clic de machine à écrire : attaque métallique très courte + petit choc grave."""
    rng = np.random.default_rng(graine)
    n = int(SR * 0.07)
    t = np.arange(n) / SR
    bruit = rng.normal(0, 1, n) * np.exp(-t * 180)
    metal = np.sin(2 * math.pi * (2400 + rng.integers(-200, 200)) * t) * np.exp(-t * 260) * 0.5
    choc = np.sin(2 * math.pi * 140 * t) * np.exp(-t * 60) * 0.6
    return (bruit * 0.55 + metal + choc) * 0.5


STYLES = {
    # typographie Da Laura (charte) : écriture manuscrite Caveat, comme l'ardoise du restaurant, qui se trace à la main
    "dalaura": dict(texte="Piatti del giorno", police=("Caveat.ttf", 176, 700), ecart=0, main=True,
                    sous=("DA LAURA  ·  la cucina autentica", ("CormorantGaramond.ttf", 44, 600), 3)),
    # version classique : capitales de l'enseigne (Cormorant Garamond), espacées, frappées à la machine
    "classique": dict(texte="PIATTI DEL GIORNO", police=("CormorantGaramond.ttf", 88, 600), ecart=7, main=False,
                      sous=("Da Laura · Cannes", ("Lato-Regular.ttf", 36, None), 4)),
}
LARGEUR_MAX = 940


def musique(duree):
    """Petite valse originale (composée ici, libre de droits), timbre d'accordéon musette, jouée très bas."""
    tempo = 0.4  # une noire
    melodie = [("G4", 1), ("C5", 1), ("E5", 1), ("E5", 2), ("D5", 1), ("F5", 1), ("A5", 1), ("F5", 1),
               ("D5", 2), ("B4", 1), ("C5", 1), ("E5", 1), ("G5", 1), ("C6", 3), ("G5", 1), ("E5", 1), ("C5", 1)]
    accords = [("C3", "E4G4C5"), ("A2", "E4A4C5"), ("D3", "F4A4D5"), ("G2", "D4G4B4"), ("C3", "E4G4C5"), ("C3", "E4G4C5"), ("G2", "D4G4B4")]
    def hz(n):
        i = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}[n[0]]
        return 440 * 2 ** ((i + 12 * (int(n[1]) - 4)) / 12)
    def note(f, d, vol):
        t = np.arange(int(SR * d)) / SR
        env = np.minimum(1, t / 0.03) * np.exp(-t * 1.2) * np.minimum(1, (d - t) / 0.05)
        son = sum(np.sin(2 * math.pi * f * k * t) / k ** 1.3 for k in range(1, 7))
        son += sum(np.sin(2 * math.pi * f * 1.004 * k * t) / k ** 1.3 for k in range(1, 7))  # voix musette désaccordée
        return son * env * vol
    out = np.zeros(int(SR * (duree + 1)))
    def poser(son, debut):
        a = int(debut * SR)
        if a < len(out):
            k = min(len(son), len(out) - a)
            out[a:a + k] += son[:k]
    t = 0.0
    for n, b in melodie:
        poser(note(hz(n), b * tempo, 0.10), t)
        t += b * tempo
    for m, (basse, acc) in enumerate(accords):
        t0 = m * 3 * tempo
        poser(note(hz(basse), tempo * 0.9, 0.12), t0)
        for k in (1, 2):
            for i in range(0, len(acc), 2):
                poser(note(hz(acc[i:i + 2]), tempo * 0.6, 0.035), t0 + k * tempo)
    out = out[: int(SR * duree)]
    tt = np.arange(len(out)) / SR
    out *= np.minimum(1, tt / 0.8) * np.minimum(1, (duree - tt) / 1.2)
    return out / (np.abs(out).max() + 1e-9) * 0.16  # très en dessous des clics de la machine


def main(photo, style, sortie):
    s = STYLES[style]
    bg = fond(photo)
    f = police(*s["police"])
    d0 = ImageDraw.Draw(bg)
    larg = [d0.textlength(c, font=f) + s["ecart"] for c in s["texte"]]
    total = sum(larg) - s["ecart"]
    while total > LARGEUR_MAX:  # le titre ne doit jamais sortir de l'écran
        nom, t, poids = s["police"]
        s["police"] = (nom, t - 4, poids)
        f = police(*s["police"])
        larg = [d0.textlength(c, font=f) + s["ecart"] for c in s["texte"]]
        total = sum(larg) - s["ecart"]
    x0, y = (W - total) / 2, 760
    debut, pas, apparition = 0.6, 0.11, 0.12
    lettres, x = [], x0
    for i, c in enumerate(s["texte"]):
        lettres.append((c, x, debut + i * pas))
        x += larg[i]
    fin_titre = debut + len(s["texte"]) * pas
    sous_txt, sous_f, sous_ecart = s["sous"]
    fs = police(*sous_f)
    duree = max(fin_titre + 2.8, 6.5)
    # voile sombre doux derrière le titre : le texte crème reste lisible même sur une photo claire
    voile = Image.new("L", (W, H), 0)
    ImageDraw.Draw(voile).ellipse([-160, y - 330, W + 160, y + 300], fill=150)
    voile = voile.filter(ImageFilter.GaussianBlur(120))
    n = int(duree * FPS)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                             "-preset", "medium", str(Path(sortie).with_suffix(".video.mp4"))], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        z = 1 + 0.04 * (t / duree)  # zoom très lent sur le fond
        bw, bh = bg.size
        cw, ch = W / z * (bw / (W * 1.06)), H / z * (bh / (H * 1.06))
        img = bg.resize((W, H), Image.BICUBIC, box=((bw - cw) / 2, (bh - ch) / 2, (bw + cw) / 2, (bh + ch) / 2)).convert("RGBA")
        img.paste((15, 10, 8, 255), (0, 0), voile)
        ombre = Image.new("L", (W, H), 0)
        txt = Image.new("L", (W, H), 0)
        do, dt = ImageDraw.Draw(ombre), ImageDraw.Draw(txt)
        if s["main"]:
            # écriture à la main : le mot entier est tracé, puis dévoilé de gauche à droite au rythme des lettres
            plein = Image.new("L", (W, H), 0)
            ImageDraw.Draw(plein).text((x0, y), s["texte"], font=f, fill=255, anchor="ls")
            xs = [cx for _, cx, _ in lettres] + [x0 + total]
            ts = [t0 for _, _, t0 in lettres] + [fin_titre]
            xm = float(np.interp(t, ts, xs)) if t >= ts[0] else -1
            m = Image.new("L", (W, H), 0)
            if xm > 0:
                ImageDraw.Draw(m).rectangle([0, 0, xm, H], fill=255)
                m = m.filter(ImageFilter.GaussianBlur(5))
            from PIL import ImageChops
            txt = ImageChops.multiply(plein, m)
            ombre = ImageChops.multiply(plein, m).point(lambda v: int(v * 0.8))
            ombre = ombre.transform((W, H), Image.AFFINE, (1, 0, -3, 0, 1, -4))
            dt, do = ImageDraw.Draw(txt), ImageDraw.Draw(ombre)
        for c, cx, t0 in ([] if s["main"] else lettres):
            if t < t0 or c == " ":
                continue
            p = min(1, (t - t0) / apparition)
            dy = int(14 * (1 - p))  # la lettre se pose, comme frappée
            a = int(255 * p)
            dt.text((cx, y + dy), c, font=f, fill=a, anchor="ls")
            do.text((cx + 3, y + dy + 4), c, font=f, fill=int(a * 0.8), anchor="ls")
        if t > fin_titre:
            p = min(1, (t - fin_titre) / 0.6)
            ligne_w = 160 * p
            dt.line([(W / 2 - ligne_w / 2, y + 60), (W / 2 + ligne_w / 2, y + 60)], fill=int(255 * p), width=3)
            sw = sum(dt.textlength(ch, font=fs) + sous_ecart for ch in sous_txt) - sous_ecart
            sx = (W - sw) / 2
            for ch in sous_txt:
                dt.text((sx, y + 130), ch, font=fs, fill=int(230 * p), anchor="ls")
                sx += dt.textlength(ch, font=fs) + sous_ecart
        img.paste((20, 14, 10, 255), (0, 0), ombre.filter(ImageFilter.GaussianBlur(6)))
        img.paste(CREME + (255,), (0, 0), txt)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    # piste son : un clic par lettre (plus doux sur les espaces), petite sonnette à la fin de la ligne
    audio = np.zeros(int(SR * duree) + SR)
    for i, (c, _, t0) in enumerate(lettres):
        cl = clic(i) * (0.45 if c == " " else 1.0)
        a = int(t0 * SR)
        audio[a:a + len(cl)] += cl
    tt = np.arange(int(SR * 0.6)) / SR
    ding = np.sin(2 * math.pi * 2093 * tt) * np.exp(-tt * 7) * 0.18
    a = int((fin_titre + 0.05) * SR)
    audio[a:a + len(ding)] += ding
    audio = audio[: int(SR * duree)] + musique(duree)
    audio = (np.clip(audio, -1, 1) * 32767 * 0.8).astype(np.int16)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "son.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio.tobytes())
        v = Path(sortie).with_suffix(".video.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(v), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(sortie)], check=True)
        v.unlink()
    print(sortie, f"{duree:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
