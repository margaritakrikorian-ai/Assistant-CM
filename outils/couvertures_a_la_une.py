"""Couvertures des stories « à la une » de Da Laura : sobres, un mot écrit au centre.

Utilisation : python3 outils/couvertures_a_la_une.py
Sortie : stories/da-laura/a-la-une/<variante>/<nom>.jpg (1080x1920, texte dans le cercle central
recadré par Instagram) + une planche d'aperçu.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parent.parent
POL = RACINE / "outils" / "polices"
SORTIE = RACINE / "stories" / "da-laura" / "a-la-une"
W, H = 1080, 1920
MOTS = ["Piatti", "Menu", "Ambiance", "La cucina", "Fêtes", "Réserver", "Jumping", "30 ans"]
VARIANTES = {
    "creme": {"fond": "#F1E6D3", "texte": "#8E1D1D", "trait": "#B8925A", "petit": "#4A3428"},
    "rouge": {"fond": "#8E1D1D", "texte": "#F1E6D3", "trait": "#F2D98B", "petit": "#F1E6D3"},
}


def police(nom, t):
    return ImageFont.truetype(str(POL / nom), t)


def couverture(mot, v):
    im = Image.new("RGB", (W, H), v["fond"])
    d = ImageDraw.Draw(im)
    cx, cy, r = W // 2, H // 2, 455
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=v["trait"], width=8)
    t = 270
    while True:
        f = police("CormorantGaramond-Italic.ttf", t)
        if d.textlength(mot, font=f) <= 700 or t <= 90:
            break
        t -= 6
    d.text((cx, cy - 10), mot, font=f, fill=v["texte"], anchor="mm")
    s = 20
    d.polygon([(cx, cy + 190 - s), (cx + s, cy + 190), (cx, cy + 190 + s), (cx - s, cy + 190)], fill=v["trait"])
    return im


def main():
    planche = Image.new("RGB", (len(MOTS) * 230 + 20, 2 * 250 + 20), "#FFFFFF")
    for j, (nv, v) in enumerate(VARIANTES.items()):
        (SORTIE / nv).mkdir(parents=True, exist_ok=True)
        for i, mot in enumerate(MOTS):
            im = couverture(mot, v)
            nom = mot.lower().replace(" ", "-").replace("ê", "e").replace("é", "e")
            im.save(SORTIE / nv / f"{nom}.jpg", quality=95, subsampling=0)
            rond = im.crop((W // 2 - 540, H // 2 - 540, W // 2 + 540, H // 2 + 540)).resize((200, 200), Image.LANCZOS)
            m = Image.new("L", (200, 200), 0)
            ImageDraw.Draw(m).ellipse((0, 0, 199, 199), fill=255)
            planche.paste(rond, (20 + i * 230, 20 + j * 250), m)
            ImageDraw.Draw(planche).text((20 + i * 230 + 100, 20 + j * 250 + 215), mot, fill="#333", anchor="mm",
                                         font=police("Lato-Regular.ttf", 20))
    planche.save(SORTIE / "apercu.jpg", quality=92)
    print("ok", SORTIE)


if __name__ == "__main__":
    main()
