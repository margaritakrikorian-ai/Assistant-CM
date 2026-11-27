"""20 modèles de stories « Piatti del giorno » SANS plats écrits (l'utilisatrice ajoute les suggestions elle-même).

    python3 outils/stories_modeles.py

Sortie : stories/da-laura/piatti-modeles/2026-12/<date>.jpg (1080x1920), une photo différente par jour,
charte naturelle, titre « Piatti del giorno », date, et un cadre crème vide où écrire les suggestions
(dans Instagram avec l'outil texte, ou dans le fichier PowerPoint modifiable généré par stories_modeles.js).
"""
import datetime
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
POL = RACINE / "outils" / "polices"
W, H = 1080, 1920
ROUGE, CREME = (142, 29, 29), (241, 230, 211)
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

# 20 stories : du mardi au samedi, sauf le 25 (fermé) remplacé par le mardi 29. Une photo différente par jour.
PROGRAMME = [
 ("2026-12-01", "burrata-prosciutto-dessus"), ("2026-12-02", "pates-ragu"), ("2026-12-03", "planche-antipasti"),
 ("2026-12-04", "spaghetti-champignons"), ("2026-12-05", "burrata-tomates"),
 ("2026-12-08", "risotto-safran-table"), ("2026-12-09", "chef-spaghetti-crevettes"), ("2026-12-10", "tartare"),
 ("2026-12-11", "langoustines-pates"), ("2026-12-12", "huile-burrata"),
 ("2026-12-15", "poelee-mer"), ("2026-12-16", "risotto-champignons"), ("2026-12-17", "gnocchi-planche"),
 ("2026-12-18", "burrata-mains"), ("2026-12-19", "poele-flamme-pates-2"),
 ("2026-12-22", "citron-zeste"), ("2026-12-23", "tiramisu-fraise"), ("2026-12-24", "table-bougie"),
 ("2026-12-26", "chef-dressage-4"), ("2026-12-29", "risotto-safran-jambon"),
]
CADRE = (110, 1150, W - 110, 1660)  # zone vide où écrire les suggestions


def police(nom, taille, poids=None):
    f = ImageFont.truetype(str(POL / nom), taille)
    if poids:
        f.set_variation_by_axes([poids])
    return f


def date_fr(d):
    j = "1er" if d.day == 1 else str(d.day)
    return f"{JOURS[d.weekday()]} {j} {MOIS[d.month - 1]}"


def modele(date, photo, sortie):
    d = datetime.date.fromisoformat(date)
    src = ImageOps.exif_transpose(Image.open(RACINE / f"photos/da-laura/cannes/{photo}.jpg")).convert("RGB")
    img = appliquer_charte(ImageOps.fit(src, (W, H), Image.LANCZOS, centering=(0.5, 0.45))).convert("RGBA")
    # léger dégradé sombre en haut pour la lisibilité du titre (la photo reste nette)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(205 * max(0, 1 - y / 820) ** 1.3))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [grad.resize((W, H))]))
    dr = ImageDraw.Draw(img)
    f_small = police("Lato-Bold.ttf", 34)
    txt = "DA LAURA  ·  CANNES"
    dr.text((W / 2, 150), txt, font=f_small, fill=CREME, anchor="mm")
    dr.text((W / 2, 290), "Piatti del giorno", font=police("PlayfairDisplay-Italic.ttf", 124), fill=(255, 250, 240), anchor="mm", stroke_width=1, stroke_fill=(40, 30, 25))
    dr.line([(W / 2 - 70, 395), (W / 2 + 70, 395)], fill=CREME, width=3)
    dr.text((W / 2, 455), date_fr(d), font=police("CormorantGaramond.ttf", 62, 600), fill=CREME, anchor="mm", stroke_width=2, stroke_fill=(40, 30, 25))
    # cadre crème vide, ombre douce
    ombre = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ombre).rounded_rectangle([CADRE[0], CADRE[1] + 18, CADRE[2], CADRE[3] + 18], 36, fill=110)
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [ombre.filter(ImageFilter.GaussianBlur(30))]))
    cadre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cadre).rounded_rectangle(CADRE, 36, fill=CREME + (238,), outline=ROUGE + (255,), width=3)
    img.alpha_composite(cadre)
    dr = ImageDraw.Draw(img)
    dr.text((W / 2, CADRE[3] + 110), "Réservations : 04 93 38 40 51", font=police("Lato-Bold.ttf", 36), fill=(255, 250, 240), anchor="mm",
            stroke_width=2, stroke_fill=(40, 30, 25))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(sortie, quality=93)


if __name__ == "__main__":
    out = RACINE / "stories/da-laura/piatti-modeles/2026-12"
    for date, photo in PROGRAMME:
        modele(date, photo, out / f"{date}.jpg")
    (out / "programme.json").write_text(json.dumps(PROGRAMME, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(PROGRAMME)} modèles dans {out.relative_to(RACINE)}")
