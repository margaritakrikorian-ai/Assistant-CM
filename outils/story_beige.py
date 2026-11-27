"""Story « Piatti del giorno » sobre : fond beige (crème de la charte #F4EDE1), écriture bordeaux (#7A1F2B), logo Da Laura.

    python3 outils/story_beige.py exemple            → stories/da-laura/piatti-beige/exemple.jpg (avec plats d'exemple)
    python3 outils/story_beige.py vide 2026-12-01    → modèle sans plats (pour écrire dans Instagram)
"""
import datetime
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent
POL = R / "outils/polices"
W, H = 1080, 1920
BEIGE, BORDEAUX, OR = (0xF4, 0xED, 0xE1), (0x7A, 0x1F, 0x2B), (0xB8, 0x92, 0x5A)
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def f(nom, t, poids=None):
    p = ImageFont.truetype(str(POL / nom), t)
    if poids:
        p.set_variation_by_axes([poids])
    return p


def story(plats, date=None):
    img = Image.new("RGB", (W, H), BEIGE)
    d = ImageDraw.Draw(img)
    logo = Image.open(R / "photos/da-laura/logo/logo-da-laura-bordeaux.png")
    lw = 400
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, ((W - lw) // 2, 150), logo)
    y = 150 + logo.height + 90
    d.text((W / 2, y), "Piatti del giorno", font=f("PlayfairDisplay-Italic.ttf", 112), fill=BORDEAUX, anchor="mm")
    y += 95
    if date:
        j = "1er" if date.day == 1 else str(date.day)
        d.text((W / 2, y), f"{JOURS[date.weekday()]} {j} {MOIS[date.month - 1]}", font=f("CormorantGaramond.ttf", 52, 600), fill=BORDEAUX, anchor="mm")
        y += 70
    d.line([(W / 2 - 80, y), (W / 2 + 80, y)], fill=OR, width=3)
    y += 110
    for nom, desc, prix in plats:
        d.text((W / 2, y), nom, font=f("CormorantGaramond.ttf", 62, 700), fill=BORDEAUX, anchor="mm")
        y += 62
        if desc:
            d.text((W / 2, y), desc, font=f("CormorantGaramond-Italic.ttf", 44, 500), fill=(110, 60, 60), anchor="mm")
            y += 56
        if prix:
            d.text((W / 2, y), prix, font=f("CormorantGaramond.ttf", 48, 600), fill=BORDEAUX, anchor="mm")
            y += 58
        y += 55
    d.line([(W / 2 - 80, H - 230), (W / 2 + 80, H - 230)], fill=OR, width=3)
    d.text((W / 2, H - 170), "Réservations : 04 93 38 40 51", font=f("Lato-Bold.ttf", 36), fill=BORDEAUX, anchor="mm")
    return img


if __name__ == "__main__":
    out = R / "stories/da-laura/piatti-beige"
    out.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "exemple":
        # plats lus sur l'ardoise du restaurant (exemple de mise en page)
        plats = [("Ravioli maison", "pomodorini freschi e burrata", "32 €"),
                 ("Polpo alla piastra", "ratatouille du chef napolitain", "34 €"),
                 ("Tagliolini aux champignons", "champignons poêlés, persil", "")]
        story(plats, datetime.date(2026, 12, 1)).save(out / "exemple.jpg", quality=94)
    else:
        dt = datetime.date.fromisoformat(sys.argv[2])
        story([], dt).save(out / f"{dt}.jpg", quality=94)
    print("ok")
