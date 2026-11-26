"""Réel « même table » : chaque plat détouré est posé en gros plan, sur le côté, sur la même table vide
(métal patiné de Da Laura, agrandie x2). La caméra glisse le long de la table d'un plat à l'autre.
Aucun texte. Charte photo naturelle appliquée aux plats.

    python3 outils/table/reel_table.py antipasti
    python3 outils/table/reel_table.py pasta
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402
from table import table  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
W, H, FPS = 1080, 1920, 30
PLATS = RACINE / "outils/table/plats"

REELS = {
    # (fichier détouré, largeur à l'écran en px, centre x en fraction de l'écran, rotation en degrés)
    "antipasti": [("burrata-prosciutto", 940, 0.5, -4), ("tartare", 960, 0.5, 3),
                  ("prosciutto-figues", 980, 0.5, -2), ("planche-fromages", 820, 0.5, 4)],
    "pasta": [("spaghetti-champignons", 980, 0.5, -3), ("fusilli-piment", 960, 0.5, 3),
              ("risotto", 960, 0.5, -3)],
}
TENUE, GLISSE = 2.6, 0.8  # secondes sur chaque plat, secondes de glissement


def doux(p):
    p = min(1.0, max(0.0, p))
    return 0.5 - 0.5 * math.cos(math.pi * p)


def lumiere(img):
    """Lumière naturelle douce : un peu plus clair en haut à gauche, coins légèrement assombris."""
    yy, xx = np.mgrid[0:img.height, 0:img.width].astype(np.float32)
    d = np.sqrt(((xx - img.width * 0.35) / img.width) ** 2 + ((yy % H - H * 0.35) / H) ** 2)
    k = np.clip(1.12 - 0.45 * d, 0.7, 1.12)[..., None]
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * k, 0, 255).astype(np.uint8))


def poser(fond, plat, largeur, cx, cy, angle):
    p = Image.open(PLATS / f"{plat}.png").convert("RGBA")
    p = p.resize((largeur, int(p.height * largeur / p.width)), Image.LANCZOS)
    rgb = appliquer_charte(p.convert("RGB"))
    rgb.putalpha(p.getchannel("A"))
    p = rgb.rotate(angle, Image.BICUBIC, expand=True)
    a = p.getchannel("A")
    ombre = Image.new("L", fond.size, 0)
    x, y = int(cx - p.width / 2), int(cy - p.height / 2)
    ombre.paste(a, (x + 22, y + 40))
    ombre = ombre.filter(ImageFilter.GaussianBlur(34)).point(lambda v: int(v * 0.62))
    noir = Image.new("RGB", fond.size, (8, 6, 5))
    fond = Image.composite(noir, fond, ombre)
    fond.paste(p, (x, y), p)
    return fond


def main(nom):
    plats = REELS[nom]
    n = len(plats)
    long_ = H * n
    fond = lumiere(table(W, long_, graine=7))
    # profondeur de champ « portrait » : la table est nette autour du plat et s'adoucit vers le haut et le bas
    flou = fond.filter(ImageFilter.GaussianBlur(14))
    yy, xx = np.mgrid[0:long_, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / 620) ** 2 + (((yy % H) - H / 2) / 560) ** 2)
    m = Image.fromarray((np.clip((d - 0.8) / 0.7, 0, 1) * 255).astype(np.uint8))
    fond = Image.composite(flou, fond, m)
    for i, (plat, larg, fx, ang) in enumerate(plats):
        fond = poser(fond, plat, larg, W * fx, H * i + H * 0.5, ang)
    sortie = RACINE / f"reels/da-laura/table/{nom}.mp4"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    total = n * TENUE + (n - 1) * GLISSE + 0.6
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-f", "lavfi", "-t", f"{total:.2f}", "-i",
                             "anullsrc=r=44100:cl=stereo", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(sortie)],
                            stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        t = f / FPS
        # position de la caméra le long de la table : tenue sur chaque plat, glissement adouci entre deux
        seg = TENUE + GLISSE
        k = min(int(t // seg), n - 1)
        local = t - k * seg
        y = H * k + (H * doux((local - TENUE) / GLISSE) if (local > TENUE and k < n - 1) else 0)
        z = 1.0 + 0.05 * doux(min(local, TENUE) / TENUE)  # léger rapprochement sur chaque plat
        cw, ch = W / z, H / z
        box = ((W - cw) / 2, y + (H - ch) / 2, (W + cw) / 2, y + (H + ch) / 2)
        img = fond.resize((W, H), Image.BICUBIC, box=box)
        if local > TENUE and k < n - 1:  # flou de mouvement vertical pendant le glissement
            force = math.sin(math.pi * (local - TENUE) / GLISSE)
            if force > 0.05:
                img = img.resize((W, max(8, int(H / (1 + 25 * force)))), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        if t < 0.5:  # ouverture en fondu depuis le noir
            img = Image.blend(Image.new("RGB", (W, H)), img, doux(t / 0.5))
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.5", "-i", str(sortie), "-frames:v", "1", "-q:v", "2",
                    str(sortie.with_name(nom + "-couverture.jpg"))], check=True)
    print(f"{sortie.relative_to(RACINE)} : {total:.1f} s, {n} plats")


if __name__ == "__main__":
    main(sys.argv[1])
