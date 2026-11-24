"""Stories « Piatti del giorno » (plats du jour) de Da Laura, au format 1080x1920.

Utilisation (depuis la racine du projet) :
    python3 outils/plats_du_jour.py plats-du-jour/da-laura-2026-12.txt
    python3 outils/plats_du_jour.py plats-du-jour/da-laura-2026-12.txt --style enseigne

Quatre styles, tous tirés de l'identité réelle du restaurant :
- suggestions (défaut, quotidien) : une photo du restaurant en fond, différente chaque jour, et les
             suggestions écrites directement dessus (titre manuscrit comme l'ardoise, plats en Cormorant) ;
- ardoise  : l'ardoise « Piatti del giorno » de la terrasse, écriture à la craie ;
- enseigne : l'enseigne « Da Laura – La cucina autentica » et la plaque « Specialità italiane, dal 1992 »,
             rouge sur crème, avec une bande de vichy comme les nappes ;
- photo    : une photo du restaurant en fond flouté, avec une carte crème.

Fichier d'entrée (texte simple, une journée par bloc, séparés par une ligne vide) :
    2026-12-01
    Ravioli maison | pomodorini freschi e burrata | 32 €
    Polpo alla piastra | ratatouille du chef | 34 €
    photo: photos/da-laura/plats/ravioli-truffe.jpg      (facultatif, pour le style photo)
    style: enseigne                                       (facultatif, pour changer le style d'un jour)
Chaque plat : « Nom | description | prix ». La description et le prix sont facultatifs.

Sortie : stories/<marque>/plats-du-jour/<date>.jpg et <date>.txt (texte pour le texte alternatif et rappel des stickers).
"""
import argparse
import datetime
import random
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

RACINE = Path(__file__).resolve().parent.parent
POL = RACINE / "outils" / "polices"
W, H = 1080, 1920

ROUGE = (142, 29, 29)       # rouge de l'enseigne (#8E1D1D)
CREME = (241, 230, 211)     # crème de l'enseigne (#F1E6D3)
ARDOISE = (40, 42, 40)
CRAIE = (246, 243, 236)
CRAIE_JAUNE = (242, 217, 139)
BRUN = (74, 52, 40)

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


# ---------- polices ----------
def police(nom, taille, poids=None):
    f = ImageFont.truetype(str(POL / nom), taille)
    if poids:
        f.set_variation_by_axes([poids])
    return f


def craie(t, gras=True):
    return police("Caveat.ttf", t, 700 if gras else 500)


def serif(t, poids=600):
    return police("CormorantGaramond.ttf", t, poids)


def serif_it(t, poids=500):
    return police("CormorantGaramond-Italic.ttf", t, poids)


# ---------- outils ----------
def date_fr(d):
    return f"{JOURS[d.weekday()].capitalize()} {d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]}"


def couper(draw, txt, f, largeur):
    mots, lignes, cur = txt.split(), [], ""
    for m in mots:
        t = (cur + " " + m).strip()
        if draw.textlength(t, font=f) <= largeur:
            cur = t
        else:
            if cur:
                lignes.append(cur)
            cur = m
    return lignes + ([cur] if cur else [])


def espace(draw, y, txt, f, fill, ecart, x0=0, x1=W):
    w = sum(draw.textlength(c, font=f) for c in txt) + ecart * (len(txt) - 1)
    x = x0 + (x1 - x0 - w) / 2
    for c in txt:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + ecart


def bruit(taille, mini, maxi, flou=0.6, graine=1):
    """Masque de grain (L) entre mini et maxi : donne l'aspect craie ou papier."""
    random.seed(graine)
    n = Image.effect_noise(taille, 64).filter(ImageFilter.GaussianBlur(flou))
    return n.point(lambda v: int(mini + (maxi - mini) * v / 255))


class Calque:
    """Texte dessiné sur un masque, puis posé avec un grain (effet craie) ou net."""

    def __init__(self):
        self.masques = {}

    def texte(self, couleur, xy, txt, f, anchor="ma"):
        m = self.masques.setdefault(couleur, Image.new("L", (W, H), 0))
        ImageDraw.Draw(m).text(xy, txt, font=f, fill=255, anchor=anchor)

    def poser(self, img, grain=None):
        for couleur, m in self.masques.items():
            if grain is not None:
                m = ImageChops.multiply(m, grain)
            img.paste(Image.new("RGB", (W, H), couleur), (0, 0), m)


def bloc_plats(plats, f_nom, f_desc, f_prix, largeur, inter):
    """Mesure le bloc des plats : renvoie la liste des lignes (texte, police, rôle) et la hauteur totale."""
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    lignes = []
    for i, (nom, desc, prix) in enumerate(plats):
        if i:
            lignes.append(("~", f_desc, "sep"))
        for l in couper(d, nom, f_nom, largeur):
            lignes.append((l, f_nom, "nom"))
        if desc:
            for l in couper(d, desc, f_desc, largeur):
                lignes.append((l, f_desc, "desc"))
        if prix:
            lignes.append((prix, f_prix, "prix"))
    h = sum(f.size * inter for _, f, _ in lignes)
    return lignes, h


def ajuster_plats(plats, polices, largeur, hmax, inter=1.18):
    """Réduit les tailles jusqu'à ce que le bloc tienne dans la hauteur disponible."""
    echelle = 1.0
    while True:
        fs = [p(max(20, int(t * echelle))) for p, t in polices]
        lignes, h = bloc_plats(plats, *fs, largeur, inter)
        if h <= hmax or echelle < 0.5:
            return lignes, h
        echelle -= 0.05


def triangle(draw, cx, y, larg, couleur, epais=3):
    """Petit triangle pointe en bas, clin d'œil à l'emblème de l'enseigne."""
    h = larg * 0.87
    pts = [(cx - larg / 2, y), (cx + larg / 2, y), (cx, y + h)]
    draw.polygon(pts, outline=couleur, width=epais)
    k = 0.62
    draw.polygon([(cx - larg * k / 2, y + 9), (cx + larg * k / 2, y + 9), (cx, y + 9 + h * k)],
                 outline=couleur, width=max(1, epais - 1))


def vichy(taille, couleur, fond, carreau=34):
    """Motif vichy (comme les nappes du restaurant)."""
    w, h = taille
    base = Image.new("RGB", taille, fond)
    bande = Image.new("RGB", taille, couleur)
    m = Image.new("L", taille, 0)
    d = ImageDraw.Draw(m)
    for x in range(0, w, carreau * 2):
        d.rectangle([x, 0, x + carreau - 1, h], fill=110)
    m2 = Image.new("L", taille, 0)
    d2 = ImageDraw.Draw(m2)
    for y in range(0, h, carreau * 2):
        d2.rectangle([0, y, w, y + carreau - 1], fill=110)
    base.paste(bande, (0, 0), m)
    base.paste(bande, (0, 0), m2)
    return base


# ---------- style 1 : l'ardoise ----------
def style_ardoise(jour, plats, _photo):
    img = Image.new("RGB", (W, H), ARDOISE)
    # texture d'ardoise : grain + traces de craie effacée
    g = bruit((W, H), 0, 22, flou=0.8, graine=2)
    img.paste(Image.new("RGB", (W, H), (90, 92, 88)), (0, 0), g)
    traces = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(traces)
    random.seed(jour.toordinal())
    for _ in range(14):
        x, y, r = random.randint(0, W), random.randint(0, H), random.randint(120, 360)
        dt.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=random.randint(8, 18))
    img.paste(Image.new("RGB", (W, H), (200, 200, 195)), (0, 0), traces.filter(ImageFilter.GaussianBlur(70)))

    c = Calque()
    d = ImageDraw.Draw(img)
    espace(d, 262, "DA LAURA", serif(50, 700), CREME, 12)
    d.text((W / 2, 326), "la cucina autentica · dal 1992", font=serif_it(34), fill=(214, 205, 188), anchor="ma")
    c.texte(CRAIE, (W / 2, 392), "Piatti del giorno", craie(148))
    c.texte(CRAIE_JAUNE, (W / 2, 572), date_fr(jour), craie(58, gras=False))

    lignes, h = ajuster_plats(plats, [(craie, 76), (lambda t: craie(t, False), 52), (craie, 64)], 860, 820)
    y = 690 + (860 - h) / 2
    for txt, f, role in lignes:
        couleur = {"nom": CRAIE, "desc": (214, 210, 200), "prix": CRAIE_JAUNE, "sep": (170, 170, 165)}[role]
        c.texte(couleur, (W / 2, y), txt, f)
        y += f.size * 1.18
    c.texte(CRAIE, (W / 2, 1596), "Réserve ta table · lien en bio", craie(48, gras=False))
    c.poser(img, bruit((W, H), 150, 255, flou=0.5, graine=3))
    triangle(ImageDraw.Draw(img), W / 2, 1530, 50, CREME, 2)
    return img


# ---------- style 2 : l'enseigne ----------
def style_enseigne(jour, plats, _photo):
    img = Image.new("RGB", (W, H), CREME)
    img.paste(Image.new("RGB", (W, H), (226, 212, 188)), (0, 0), bruit((W, H), 0, 40, flou=1.2, graine=4))
    bande = vichy((W, 150), ROUGE, CREME)
    img.paste(bande, (0, 0))
    img.paste(bande, (0, H - 150))
    d = ImageDraw.Draw(img)
    # double cadre rouge, comme le bord de l'enseigne
    d.rectangle([60, 210, W - 60, H - 210], outline=ROUGE, width=6)
    d.rectangle([76, 226, W - 76, H - 226], outline=ROUGE, width=2)

    espace(d, 290, "DA LAURA", serif(46, 700), ROUGE, 12)
    d.text((W / 2, 350), "la cucina autentica", font=serif_it(36), fill=BRUN, anchor="ma")
    d.text((W / 2, 420), "PIATTI DEL GIORNO", font=serif(86, 700), fill=ROUGE, anchor="ma")
    d.text((W / 2, 528), date_fr(jour), font=serif_it(46), fill=BRUN, anchor="ma")
    d.rectangle([W / 2 - 70, 600, W / 2 + 70, 603], fill=ROUGE)

    lignes, h = ajuster_plats(plats, [(lambda t: serif(t, 700), 64), (lambda t: serif_it(t, 500), 46),
                                      (lambda t: serif(t, 700), 54)], 820, 840)
    y = 650 + (880 - h) / 2
    for txt, f, role in lignes:
        if role == "sep":
            d.polygon([(W / 2, y + 14), (W / 2 + 10, y + 24), (W / 2, y + 34), (W / 2 - 10, y + 24)], fill=ROUGE)
        else:
            couleur = {"nom": (43, 33, 28), "desc": BRUN, "prix": ROUGE}[role]
            d.text((W / 2, y), txt, font=f, fill=couleur, anchor="ma")
        y += f.size * 1.18
    # plaque « Specialità italiane · dal 1992 »
    d.rounded_rectangle([W / 2 - 250, 1560, W / 2 + 250, 1660], radius=14, fill=ROUGE)
    d.rounded_rectangle([W / 2 - 240, 1570, W / 2 + 240, 1650], radius=10, outline=CREME, width=2)
    d.text((W / 2, 1582), "Specialità italiane · dal 1992", font=serif(40, 600), fill=CREME, anchor="ma")
    return img


# ---------- style 3 : la photo ----------
def style_photo(jour, plats, photo):
    if photo and (RACINE / photo).exists():
        fond = ImageOps.fit(ImageOps.exif_transpose(Image.open(RACINE / photo)).convert("RGB"), (W, H), Image.LANCZOS)
        fond = fond.filter(ImageFilter.GaussianBlur(16))
        fond = Image.blend(fond, Image.new("RGB", (W, H), (20, 14, 10)), 0.35)
    else:
        fond = Image.new("RGB", (W, H), (60, 40, 32))
    img = fond
    carte = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(carte)
    dc.rounded_rectangle([90, 300, W - 90, 1640], radius=36, fill=CREME + (244,))
    img.paste(carte, (0, 0), carte)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([106, 316, W - 106, 1624], radius=28, outline=ROUGE, width=2)
    espace(d, 372, "DA LAURA", serif(44, 700), ROUGE, 12)
    c = Calque()
    c.texte(ROUGE, (W / 2, 428), "Piatti del giorno", craie(128))
    c.poser(img)
    d.text((W / 2, 588), date_fr(jour), font=serif_it(46), fill=BRUN, anchor="ma")
    lignes, h = ajuster_plats(plats, [(lambda t: serif(t, 700), 60), (lambda t: serif_it(t, 500), 44),
                                      (lambda t: serif(t, 700), 52)], 780, 780)
    y = 680 + (800 - h) / 2
    for txt, f, role in lignes:
        if role == "sep":
            d.polygon([(W / 2, y + 14), (W / 2 + 9, y + 23), (W / 2, y + 32), (W / 2 - 9, y + 23)], fill=ROUGE)
        else:
            d.text((W / 2, y), txt, font=f, fill={"nom": (43, 33, 28), "desc": BRUN, "prix": ROUGE}[role], anchor="ma")
        y += f.size * 1.18
    d.text((W / 2, 1530), "Réserve ta table · lien en bio", font=serif_it(40), fill=ROUGE, anchor="ma")
    return img


# ---------- style 4 : les suggestions sur photo (style quotidien par défaut) ----------
DOSSIERS_FOND = ["ambiance", "plats", "cuisine"]
EXT = (".jpg", ".jpeg", ".png", ".webp")


def photo_du_jour(jour, marque="da-laura"):
    """Choisit une photo de fond différente chaque jour, en tournant sur les photos du restaurant."""
    photos = sorted(p for d in DOSSIERS_FOND for p in (RACINE / "photos" / marque / d).glob("*")
                    if p.suffix.lower() in EXT)
    return photos[jour.toordinal() % len(photos)] if photos else None


def style_suggestions(jour, plats, photo):
    chemin = (RACINE / photo) if photo else photo_du_jour(jour)
    if chemin and chemin.exists():
        fond = ImageOps.fit(ImageOps.exif_transpose(Image.open(chemin)).convert("RGB"), (W, H), Image.LANCZOS,
                            centering=(0.5, 0.45))
        fond = fond.filter(ImageFilter.GaussianBlur(5))  # léger flou : la photo reste reconnaissable
    else:
        fond = Image.new("RGB", (W, H), (70, 48, 36))
    # voile sombre, plus marqué derrière le texte, pour une lecture parfaite
    voile = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(voile)
    for y in range(H):
        centre = 1 - min(1, abs(y - 960) / 900)
        dv.line([(0, y), (W, y)], fill=int(70 + 80 * centre))
    img = Image.composite(Image.new("RGB", (W, H), (18, 12, 8)), fond, voile)

    # titre et plats : texte avec une ombre douce
    ombre = Image.new("L", (W, H), 0)
    c = Calque()

    def ecrire(couleur, xy, txt, f):
        c.texte(couleur, xy, txt, f)
        ImageDraw.Draw(ombre).text((xy[0] + 2, xy[1] + 3), txt, font=f, fill=150, anchor="ma")

    ecrire(CREME, (W / 2, 300), "Piatti del giorno", craie(140))
    ecrire((232, 220, 198), (W / 2, 478), f"Les suggestions du {date_fr(jour).split(' ', 1)[1]}", serif_it(46))

    lignes, h = ajuster_plats(plats, [(lambda t: serif(t, 600), 60), (lambda t: serif_it(t, 500), 46),
                                      (lambda t: serif(t, 700), 50)], 860, 900)
    y = 600 + (940 - h) / 2
    for txt, f, role in lignes:
        if role == "sep":
            ecrire((214, 196, 160), (W / 2, y - 6), "~", craie(60))
        else:
            ecrire({"nom": (250, 246, 238), "desc": (230, 220, 202), "prix": (242, 217, 139)}[role], (W / 2, y), txt, f)
        y += f.size * 1.18

    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), ombre.filter(ImageFilter.GaussianBlur(6)))
    c.poser(img)
    d = ImageDraw.Draw(img)
    triangle(d, W / 2, 1548, 46, CREME, 2)
    espace(d, 1606, "DA LAURA", serif(34, 700), CREME, 9)
    d.text((W / 2, 1650), "la cucina autentica · dal 1992", font=serif_it(28), fill=(220, 208, 186), anchor="ma")
    return img


STYLES = {"suggestions": style_suggestions, "ardoise": style_ardoise, "enseigne": style_enseigne, "photo": style_photo}


# ---------- lecture du fichier ----------
def lire(fichier):
    jours, cur = [], None
    for brut in Path(fichier).read_text(encoding="utf-8").splitlines():
        l = brut.strip()
        if not l or l.startswith("#"):
            cur = None if not l else cur
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", l):
            cur = {"date": datetime.date.fromisoformat(l), "plats": [], "photo": None, "style": None}
            jours.append(cur)
        elif cur is None:
            raise SystemExit(f"Ligne hors d'une journée (ajoutez d'abord une date AAAA-MM-JJ) : {l}")
        elif l.lower().startswith("photo:"):
            cur["photo"] = l.split(":", 1)[1].strip()
        elif l.lower().startswith("style:"):
            cur["style"] = l.split(":", 1)[1].strip().lower()
        else:
            parts = [p.strip() for p in l.split("|")] + ["", ""]
            cur["plats"].append(tuple(parts[:3]))
    return jours


def main():
    ap = argparse.ArgumentParser(description="Stories « Piatti del giorno » de Da Laura.")
    ap.add_argument("fichier", help="ex. plats-du-jour/da-laura-2026-12.txt")
    ap.add_argument("--style", choices=STYLES, default="suggestions")
    ap.add_argument("--marque", default="da-laura")
    ap.add_argument("--sortie", help="dossier de sortie (défaut : stories/<marque>/plats-du-jour)")
    a = ap.parse_args()
    sortie = Path(a.sortie) if a.sortie else RACINE / "stories" / a.marque / "plats-du-jour"
    sortie.mkdir(parents=True, exist_ok=True)
    jours = lire(a.fichier)
    for j in jours:
        style = j["style"] or a.style
        img = STYLES[style](j["date"], j["plats"], j["photo"])
        nom = sortie / f"{j['date'].isoformat()}"
        img.save(nom.with_suffix(".jpg"), quality=95, subsampling=0)
        plats_txt = "\n".join("- " + " · ".join(p for p in pl if p) for pl in j["plats"])
        nom.with_suffix(".txt").write_text(
            f"Story « Piatti del giorno » · {date_fr(j['date'])} · style {style}\n\n"
            f"Texte alternatif : Les plats du jour de Da Laura.\n{plats_txt}\n\n"
            "À ajouter dans Instagram : sticker « Lien » vers la réservation, sticker « Lieu » : Cannes.\n"
            "Hashtags : #DaLaura + sticker localisation « Cannes »\n", encoding="utf-8")
        print(f"{nom.with_suffix('.jpg')} ({style}, {len(j['plats'])} plats)")
    print(f"{len(jours)} stories créées.")


if __name__ == "__main__":
    main()
