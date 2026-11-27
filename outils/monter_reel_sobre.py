"""Réel sobre et élégant, SANS AUCUN TEXTE (choix de l'utilisatrice, 26/11/2026) : photos plein écran,
mouvement lent (zoom ou glissement), transitions fluides (fondu, glissé, zoom), charte photo naturelle.
Piste audio silencieuse : la musique s'ajoute dans Instagram ou TikTok.

    python3 outils/monter_reel_sobre.py outils/reels/<plan>.json [--tiktok]

Plan JSON : {"photos": [chemin, ou {"source": chemin, "centre": [x, y]}...], "sortie": "reels/da-laura/x.mp4",
             "legende", "hashtags", "legende_tiktok", "hashtags_tiktok"}
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
TRANSITIONS = ["fade", "smoothleft", "fade", "zoomin", "smoothup", "fade", "smoothright", "fadewhite"]
MOUVEMENTS = ["zoom-avant", "gauche-droite", "zoom-arriere", "droite-gauche"]


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)


def clip(p, i, duree, sortie):
    p = p if isinstance(p, dict) else {"source": p}
    src = ImageOps.exif_transpose(Image.open(RACINE / p["source"])).convert("RGB")
    img = ImageOps.fit(src, (W * 2, H * 2), Image.LANCZOS, centering=tuple(p.get("centre", [0.5, 0.5])))
    img = appliquer_charte(img.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=2)))
    png = sortie.with_suffix(".png")
    img.save(png)
    n, a = int(round(duree * FPS)), 0.10
    m = p.get("mouvement", MOUVEMENTS[i % len(MOUVEMENTS)])
    lisse = f"(0.5-0.5*cos(PI*on/{n}))"
    if m == "zoom-avant":
        z, x, y = f"1+{a}*{lisse}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif m == "zoom-arriere":
        z, x, y = f"1+{a}-{a}*{lisse}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif m == "gauche-droite":
        z, x, y = f"1+{a}", f"(iw-iw/zoom)*{lisse}", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = f"1+{a}", f"(iw-iw/zoom)*(1-{lisse})", "ih/2-(ih/zoom/2)"
    ff(["-i", str(png), "-vf", f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p",
        "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "17", str(sortie)])


def main(fichier, tiktok=False):
    plan = json.loads(Path(fichier).read_text(encoding="utf-8"))
    duree, tr = (1.5, 0.4) if tiktok else (2.2, 0.6)
    sortie = RACINE / plan["sortie"]
    if tiktok:
        sortie = sortie.with_name(sortie.stem + "-tiktok.mp4")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    photos = plan["photos"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips = []
        for i, p in enumerate(photos):
            c = tmp / f"c{i:02d}.mp4"
            clip(p, i, duree, c)
            clips.append(c)
        entrees = sum((["-i", str(c)] for c in clips), [])
        filtres, cur, t = [], "[0:v]", duree
        for i in range(1, len(clips)):
            off = t - tr
            filtres.append(f"{cur}[{i}:v]xfade=transition={TRANSITIONS[(i - 1) % len(TRANSITIONS)]}:duration={tr}:offset={off:.3f}[x{i}]")
            cur, t = f"[x{i}]", off + duree
        filtres.append(f"{cur}fade=t=in:d=0.4,fade=t=out:st={t - 0.5:.3f}:d=0.5,format=yuv420p[v]")
        ff(entrees + ["-f", "lavfi", "-t", f"{t:.2f}", "-i", "anullsrc=r=44100:cl=stereo",
                      "-filter_complex", ";".join(filtres), "-map", "[v]", "-map", f"{len(clips)}:a",
                      "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
                      "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "128k", "-shortest",
                      "-movflags", "+faststart", str(sortie)])
    ff(["-ss", "0.8", "-i", str(sortie), "-frames:v", "1", "-q:v", "2", str(sortie.with_name(sortie.stem + "-couverture.jpg"))])
    leg = plan.get("legende_tiktok" if tiktok else "legende", plan["legende"])
    tags = plan.get("hashtags_tiktok" if tiktok else "hashtags", plan["hashtags"])
    sortie.with_suffix(".txt").write_text(leg.strip() + "\n\n" + tags + "\n", encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} : {t:.1f} s, {len(photos)} photos, sans texte")


if __name__ == "__main__":
    main(sys.argv[1], tiktok="--tiktok" in sys.argv[2:])
