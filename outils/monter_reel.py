"""Monte un réel dynamique (MP4 1080x1920, 30 i/s) à partir de VOS photos et vidéos.

Utilisation :
    python3 outils/monter_reel.py outils/reels/decouverte-da-laura.json

Le plan de montage (fichier JSON) décrit :
- les plans, dans l'ordre : photo animée (zoom avant, zoom arrière, glissement) ou extrait de vidéo ;
- les textes qui apparaissent par-dessus (écriture « craie » de l'ardoise) ;
- la carte de fin (adresse, réservations) ;
- la légende et les hashtags.

Ce qui est appliqué automatiquement :
- la charte photo Da Laura sur chaque image ET chaque vidéo (même filtre, via outils/charte-da-laura-hald.png) ;
- un recadrage vertical 9:16 sans déformation, une accentuation de netteté ;
- des coupes franches et rythmées (1 à 2 s par plan), comme les réels qui fonctionnent ;
- une piste audio silencieuse : la musique s'ajoute dans Instagram ou TikTok.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402
from plats_du_jour import CREME, ROUGE, BRUN, craie, espace, papier, serif, serif_it, vichy  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
HALD = RACINE / "outils" / "charte-da-laura-hald.png"
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)


def plan_photo(p, sortie):
    """Photo animée : préparée en 2x (charte + netteté) puis zoom ou glissement lent."""
    src = ImageOps.exif_transpose(Image.open(RACINE / p["source"])).convert("RGB")
    cx, cy = p.get("centre", [0.5, 0.45])
    img = ImageOps.fit(src, (W * 2, H * 2), Image.LANCZOS, centering=(cx, cy))
    img = img.filter(ImageFilter.UnsharpMask(radius=2.4, percent=70, threshold=2))
    img = appliquer_charte(img)
    tmp = sortie.with_suffix(".png")
    img.save(tmp)
    n = int(round(p["duree"] * FPS))
    a = p.get("ampleur", 0.10)
    mouvement = p.get("mouvement", "zoom-avant")
    if mouvement == "zoom-avant":
        z, x, y = f"1+{a}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mouvement == "zoom-arriere":
        z, x, y = f"1+{a}-{a}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mouvement == "gauche-droite":
        z, x, y = f"1+{a}", f"(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"
    else:  # droite-gauche
        z, x, y = f"1+{a}", f"(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"
    ff(["-i", str(tmp), "-vf", f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},setsar=1",
        "-frames:v", str(n)] + X264 + [str(sortie)])


def plan_video(p, sortie):
    """Extrait de vidéo : découpé, recadré en 9:16, passé à la charte, net."""
    d = p["fin"] - p["debut"]
    vf = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
          "unsharp=5:5:0.6,format=rgb24[v];[v][1:v]haldclut,setsar=1")
    if p.get("ralenti"):
        vf = f"setpts={p['ralenti']}*PTS," + vf
        d *= p["ralenti"]
    ff(["-ss", str(p["debut"]), "-t", str(p["fin"] - p["debut"]), "-i", str(RACINE / p["source"]),
        "-i", str(HALD), "-filter_complex", f"[0:v]{vf}", "-an", "-t", f"{d:.3f}"] + X264 + [str(sortie)])


def calque_texte(t, sortie):
    """Texte à la craie (écriture de l'ardoise) avec ombre douce, dans le tiers haut de l'image."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre = Image.new("L", (W, H), 0)
    texte = Image.new("L", (W, H), 0)
    petit = Image.new("L", (W, H), 0)
    y = t.get("y", 360)
    for calque, coul in ((ombre, 170), (texte, 255)):
        dc = ImageDraw.Draw(calque)
        dy = 4 if calque is ombre else 0
        if t.get("surtitre"):
            espace(ImageDraw.Draw(petit if calque is texte else ombre), y + dy, t["surtitre"], serif(44, 700), coul, 12)
        yy = y + (80 if t.get("surtitre") else 0)
        # taille adaptée : aucune ligne ne doit dépasser la largeur utile (marges de 70 px)
        taille = t.get("taille", 112)
        while taille > 60 and max(dc.textlength(l, font=craie(taille)) for l in t["texte"].split("\n")) > W - 140:
            taille -= 4
        for ligne in t["texte"].split("\n"):
            dc.text((W / 2 + (3 if calque is ombre else 0), yy + dy), ligne, font=craie(taille),
                    fill=coul, anchor="ma")
            yy += int(taille * 1.05)
    img.paste((0, 0, 0, 255), (0, 0), ombre.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, v * 1.2)))
    img.paste((0, 0, 0, 255), (0, 0), ombre.filter(ImageFilter.GaussianBlur(5)).point(lambda v: v * 0.9))
    img.paste(CREME + (255,), (0, 0), texte)
    img.paste((235, 222, 200, 255), (0, 0), petit)
    img.save(sortie)


def carte_fin(f, sortie):
    img = papier()
    img.paste(vichy((W, 150), ROUGE, CREME), (0, 0))
    img.paste(vichy((W, 150), ROUGE, CREME), (0, H - 150))
    d = ImageDraw.Draw(img)
    espace(d, 500, "DA LAURA", serif(130, 700), ROUGE, 24)
    d.text((W / 2, 680), "la cucina autentica · dal 1992", font=serif_it(60), fill=BRUN, anchor="ma")
    d.rectangle([W / 2 - 80, 800, W / 2 + 80, 804], fill=ROUGE)
    d.text((W / 2, 860), f.get("appel", "Réserve ta table"), font=craie(140), fill=ROUGE, anchor="ma")
    y = 1090
    for ligne in f["lignes"]:
        d.text((W / 2, y), ligne, font=serif(64, 700), fill=(43, 33, 28), anchor="ma")
        y += 90
    img.save(sortie)


def version_tiktok(plan):
    """Dérive la version TikTok d'un plan Instagram : plans ~40 % plus courts, textes plus gros,
    accroche et légende propres à TikTok, carte de fin courte."""
    import copy
    t = copy.deepcopy(plan)
    t["sortie"] = plan["sortie"].replace(".mp4", "-tiktok.mp4")
    for p in t["plans"]:
        if p["type"] == "photo":
            p["duree"] = max(0.6, round(p["duree"] * 0.62, 2))
            p["ampleur"] = p.get("ampleur", 0.1) + 0.04
        else:
            p["fin"] = round(p["debut"] + max(0.6, (p["fin"] - p["debut"]) * 0.65), 2)
    for k, tx in enumerate(t.get("textes", [])):
        tx["taille"] = tx.get("taille", 120) + 14
        if k == 0 and plan.get("accroche_tiktok"):
            tx["texte"] = plan["accroche_tiktok"]
            tx.pop("surtitre", None)
    t["fin"]["duree"] = 2.0
    t["fin"]["appel"] = plan["fin"].get("appel_tiktok", "On t'attend !")
    t["legende"] = plan.get("legende_tiktok", plan["legende"])
    t["hashtags"] = plan.get("hashtags_tiktok", plan["hashtags"])
    return t


def main(fichier_plan, tiktok=False):
    plan = json.loads(Path(fichier_plan).read_text(encoding="utf-8"))
    if tiktok:
        plan = version_tiktok(plan)
    sortie = RACINE / plan["sortie"]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips, t, bornes = [], 0.0, []
        for i, p in enumerate(plan["plans"]):
            c = tmp / f"plan{i:02d}.mp4"
            (plan_photo if p["type"] == "photo" else plan_video)(p, c)
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        str(c)], capture_output=True, text=True).stdout)
            clips.append(c)
            bornes.append((t, t + dur))
            t += dur
        for tx in plan.get("textes", []):  # textes calés sur des plans : {"plans": [premier, dernier]}
            if "plans" in tx:
                tx["debut"] = round(bornes[tx["plans"][0]][0], 2)
                tx["fin"] = round(bornes[tx["plans"][1]][1], 2)
        fin = tmp / "fin.png"
        carte_fin(plan["fin"], fin)
        c = tmp / "fin.mp4"
        n = int(plan["fin"].get("duree", 2.6) * FPS)
        ff(["-loop", "1", "-i", str(fin), "-vf", f"zoompan=z='1+0.02*on/{n}':d={n}:s={W}x{H}:fps={FPS},fade=t=in:d=0.25",
            "-frames:v", str(n)] + X264 + [str(c)])
        clips.append(c)
        total = t + n / FPS
        (tmp / "liste.txt").write_text("".join(f"file '{c}'\n" for c in clips))
        ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "liste.txt"), "-c", "copy", str(tmp / "brut.mp4")])

        # textes par-dessus, avec fondu d'apparition et de disparition
        entrees, filtres, cur = ["-i", str(tmp / "brut.mp4")], [], "[0:v]"
        for k, tx in enumerate(plan.get("textes", []), 1):
            png = tmp / f"texte{k}.png"
            calque_texte(tx, png)
            entrees += ["-loop", "1", "-t", f"{total:.2f}", "-i", str(png)]
            a, b = tx["debut"], tx["fin"]
            filtres.append(f"[{k}:v]format=rgba,fade=t=in:st={a}:d=0.25:alpha=1,fade=t=out:st={b - 0.25}:d=0.25:alpha=1[t{k}]")
            filtres.append(f"{cur}[t{k}]overlay=0:0:enable='between(t,{a},{b})'[v{k}]")
            cur = f"[v{k}]"
        entrees += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
        na = len(plan.get("textes", [])) + 1
        filtres.append(f"{cur}format=yuv420p[vf]")
        ff(entrees + ["-filter_complex", ";".join(filtres), "-map", "[vf]", "-map", f"{na}:a"] + X264 +
           ["-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "128k", "-shortest",
            "-movflags", "+faststart", str(sortie)])
        # couverture : la première image avec le premier texte
        ff(["-i", str(sortie), "-vf", "select=eq(n\\,12)", "-frames:v", "1", "-q:v", "2",
            str(sortie.with_name(sortie.stem + "-couverture.jpg"))])
    sortie.with_suffix(".txt").write_text(plan["legende"].strip() + "\n\n" + plan["hashtags"] + "\n", encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} : {total:.1f} s, {len(plan['plans'])} plans + carte de fin")


if __name__ == "__main__":
    # python3 outils/monter_reel.py <plan.json> [--tiktok]   (--tiktok : version TikTok dérivée automatiquement)
    main(sys.argv[1], tiktok="--tiktok" in sys.argv[2:])
