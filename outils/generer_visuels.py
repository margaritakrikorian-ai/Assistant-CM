"""Génère les visuels des posts et des stories à partir d'un calendrier éditorial CSV.

Utilisation (depuis la racine du projet) :
    python3 outils/generer_visuels.py calendriers/da-laura-2026-12.csv

- Posts et carrousels : 1080x1350, dans publications/<marque>/<date>-<sujet>/
  (visuel-01.jpg, visuel-02.jpg… + legende.txt)
- Stories : 1080x1920, dans stories/<marque>/<date>-<sujet>-<n>.jpg (+ .txt à côté)
- Les réels (vidéo) ne sont pas traités.

Si une photo indiquée dans le calendrier n'existe pas encore, le visuel est créé
avec un cadre « PHOTO À FOURNIR ». Ajoutez la photo au chemin indiqué puis relancez
le script : les visuels sont recréés avec la vraie photo.

Photos des stories : photos/<marque>/stories/<AAAA-MM-JJ>-<n>.jpg (n = 1, 2, 3).
À défaut, la première photo du post du même jour est utilisée.
"""
import csv
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
POLICES = RACINE / "outils" / "polices"

# Couleurs de la fiche marques/da-laura.md
ROUGE = (122, 31, 43)     # #7A1F2B
CREME = (244, 237, 225)   # #F4EDE1
OLIVE = (92, 107, 60)     # #5C6B3C
OR = (184, 146, 90)       # #B8925A

POST = (1080, 1350)
STORY = (1080, 1920)
EXT_PHOTO = (".jpg", ".jpeg", ".png", ".webp", ".heic")


# ---------- polices ----------
def titre(taille):
    f = ImageFont.truetype(str(POLICES / "PlayfairDisplay.ttf"), taille)
    f.set_variation_by_axes([700])
    return f


def texte(taille, gras=False):
    return ImageFont.truetype(str(POLICES / ("Lato-Bold.ttf" if gras else "Lato-Regular.ttf")), taille)


# ---------- outils ----------
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]")


def sans_emoji(s):
    return re.sub(r"\s{2,}", " ", EMOJI.sub("", s)).strip()


def slug(s):
    s = s.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c")):
        for c in a:
            s = s.replace(c, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def trouver(chemin):
    """Retourne le fichier photo existant (extension libre), ou None."""
    p = RACINE / chemin
    if p.exists():
        return p
    for ext in EXT_PHOTO:
        q = p.with_suffix(ext)
        if q.exists():
            return q
    return None


def photos_du_post(champ):
    """'À fournir : photos/x/salle-noel-01.jpg à -05.jpg — description' -> ([chemins], description)."""
    champ = re.sub(r"^À fournir\s*:\s*", "", champ)
    chemin, _, desc = champ.partition(" — ")
    if " + " in chemin:  # liste explicite : « photos/a.jpg + photos/b.jpg »
        return [c.strip() for c in chemin.split(" + ")], desc.strip()
    m = re.match(r"(.+)-(\d+)(\.\w+) à -(\d+)\.\w+$", chemin.strip())
    if m:
        base, debut, ext, fin = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        return [f"{base}-{i:02d}{ext}" for i in range(debut, fin + 1)], desc.strip()
    return [chemin.strip()], desc.strip()


def lignes(draw, txt, police, largeur):
    mots, res, cur = txt.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if draw.textlength(essai, font=police) <= largeur:
            cur = essai
        else:
            if cur:
                res.append(cur)
            cur = m
    if cur:
        res.append(cur)
    return res


def ajuster(draw, txt, largeur, taille_max, lignes_max=2):
    t = taille_max
    while t > 30:
        p = titre(t)
        ls = lignes(draw, txt, p, largeur)
        if len(ls) <= lignes_max:
            return p, ls
        t -= 4
    return titre(30), lignes(draw, txt, titre(30), largeur)


def espace(draw, xy, txt, police, fill, ecart=4, centre=True, largeur=None):
    """Texte avec espacement des lettres (pour les petites capitales)."""
    w = sum(draw.textlength(c, font=police) for c in txt) + ecart * (len(txt) - 1)
    x, y = xy
    if centre:
        x = x + (largeur - w) / 2
    for c in txt:
        draw.text((x, y), c, font=police, fill=fill)
        x += draw.textlength(c, font=police) + ecart


# ---------- fond : photo ou cadre « à fournir » ----------
def fond(taille, photo, chemin_attendu, description):
    if photo:
        img = Image.open(photo)
        img = ImageOps.exif_transpose(img).convert("RGB")
        # recadrage centré sans déformation, ré-échantillonnage de qualité (photo nette)
        img = ImageOps.fit(img, taille, method=Image.LANCZOS, centering=(0.5, 0.45))
        return appliquer_charte(img), False  # même rendu de couleur sur toutes les photos
    w, h = taille
    img = Image.new("RGB", taille, CREME)
    d = ImageDraw.Draw(img)
    for x in range(-h, w, 48):  # hachures légères vert olive
        d.line([(x, 0), (x + h, h)], fill=(228, 224, 206), width=2)
    m = 70
    d.rectangle([m, m, w - m, h - m], outline=OR, width=3)
    cy = h * 0.36
    espace(d, (0, cy), "PHOTO À FOURNIR", texte(40, True), OLIVE, ecart=6, largeur=w)
    y = cy + 80
    for l in lignes(d, str(chemin_attendu), texte(28), w - 2 * m - 80):
        d.text((w / 2, y), l, font=texte(28), fill=ROUGE, anchor="ma")
        y += 40
    y += 20
    for l in lignes(d, description, texte(30), w - 2 * m - 120)[:5]:
        d.text((w / 2, y), l, font=texte(30), fill=OLIVE, anchor="ma")
        y += 44
    return img, True


# ---------- habillage ----------
def bandeau_post(img, titre_txt, mention=None, petit=False):
    """Bandeau crème en bas : la photo reste intacte sur les 4/5 supérieurs."""
    w, h = img.size
    d = ImageDraw.Draw(img)
    hb = 150 if petit else 270
    if mention:
        hb += 40
    y0 = h - hb
    d.rectangle([0, y0, w, h], fill=CREME)
    d.rectangle([0, y0, w, y0 + 6], fill=OR)
    if petit:
        espace(d, (0, y0 + 58), "DA LAURA  ·  CANNES", texte(26, True), OLIVE, ecart=5, largeur=w)
    else:
        espace(d, (0, y0 + 38), "DA LAURA  ·  CANNES", texte(24, True), OLIVE, ecart=5, largeur=w)
        p, ls = ajuster(d, titre_txt, w - 160, 76)
        lh = p.size * 1.15
        y = y0 + 38 + 30 + (hb - 38 - 30 - (40 if mention else 0) - lh * len(ls)) / 2 - 6
        for l in ls:
            d.text((w / 2, y), l, font=p, fill=ROUGE, anchor="ma")
            y += lh
    if mention:
        d.text((w / 2, h - 34), mention, font=texte(22), fill=OLIVE, anchor="ma")
    return img


def carte_story(img, titre_txt, mention=None):
    """Carte crème au-dessus de la zone basse réservée par Instagram (250 px)."""
    w, h = img.size
    d = ImageDraw.Draw(img)
    p, ls = ajuster(d, titre_txt, w - 260, 84, lignes_max=3)
    lh = p.size * 1.15
    hc = 70 + 34 + 30 + lh * len(ls) + 50 + (40 if mention else 0)
    x0, x1 = 90, w - 90
    y1 = h - 300
    y0 = y1 - hc
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=CREME)
    d.rounded_rectangle([x0 + 14, y0 + 14, x1 - 14, y1 - 14], radius=20, outline=OR, width=2)
    espace(d, (x0, y0 + 56), "DA LAURA  ·  CANNES", texte(26, True), OLIVE, ecart=5, largeur=x1 - x0)
    y = y0 + 56 + 34 + 34
    for l in ls:
        d.text((w / 2, y), l, font=p, fill=ROUGE, anchor="ma")
        y += lh
    if mention:
        d.text((w / 2, y1 - 56), mention, font=texte(22), fill=OLIVE, anchor="ma")
    return img


def enregistrer(img, chemin):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    img.save(chemin, "JPEG", quality=95, subsampling=0, optimize=True)


# ---------- stories : extraire le texte de chaque écran ----------
def ecrans_story(sequence):
    """'1. Vidéo …, texte « Décembre ✨ »\\n2. Sondage « Prêt ? » Oui / Non\\n3. Partage du post' ->
    [(n, consigne, texte_visuel ou None)]"""
    res = []
    for l in sequence.split("\n"):
        m = re.match(r"\s*(\d+)\.\s*(.+)", l)
        if not m:
            continue
        n, consigne = int(m.group(1)), m.group(2).strip()
        q = re.search(r"«\s*(.+?)\s*»", consigne)
        if consigne.lower().startswith("partage"):
            res.append((n, consigne, None))  # se fait directement dans Instagram
        else:
            res.append((n, consigne, sans_emoji(q.group(1)) if q else None))
    return res


def a_ajouter(consigne):
    c = consigne.lower()
    for mot, quoi in (("sondage", "sticker « Sondage »"), ("quiz", "sticker « Quiz »"),
                      ("boîte à questions", "sticker « Questions »"), ("compte à rebours", "sticker « Compte à rebours »"),
                      ("lien", "sticker « Lien » vers la page de réservation"), ("localisation", "sticker « Lieu » : Cannes")):
        if mot in c:
            return quoi
    return None


# ---------- programme principal ----------
def main(csv_path, marque=None, sortie=None):
    """sortie : dossier où ranger publications/ et stories/ (par défaut : racine du projet, rangé par marque)."""
    csv_path = Path(csv_path)
    marque = marque or re.match(r"(.+)-\d{4}-\d{2}$", csv_path.stem).group(1)
    if sortie:
        base_pub, base_story = Path(sortie) / "publications", Path(sortie) / "stories"
    else:
        base_pub, base_story = RACINE / "publications" / marque, RACINE / "stories" / marque
    with open(RACINE / csv_path if not csv_path.is_absolute() else csv_path, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))

    posts_du_jour = {}
    bilan = {"posts": 0, "stories": 0, "attente": 0}
    EVIN = "L'abus d'alcool est dangereux pour la santé, à consommer avec modération."

    for r in rows:
        j, mo, a = r["Date"].split("/")
        date = f"{a}-{mo}-{j}"
        if r["Format"].startswith("Story"):
            continue
        chemins, desc = photos_du_post(r["Photo / vidéo"])
        sujet = re.sub(r"-\d+$", "", Path(chemins[0]).stem)
        if r["Format"] not in ("Post", "Carrousel"):  # réel : vidéo, pas de visuel
            posts_du_jour[date] = (sujet, [])
            continue
        dossier = base_pub / f"{date}-{sujet}"
        posts_du_jour[date] = (sujet, chemins)
        mention = EVIN if "abus d'alcool" in r["Légende"] else None
        for i, ch in enumerate(chemins, 1):
            img, attente = fond(POST, trouver(ch), ch, desc)
            img = bandeau_post(img, r["Texte visuel"], mention, petit=i > 1)
            enregistrer(img, dossier / f"visuel-{i:02d}.jpg")
            bilan["posts"] += 1
            bilan["attente"] += attente
        (dossier / "legende.txt").write_text(r["Légende"] + "\n\n" + r["Hashtags"] + "\n", encoding="utf-8")
        marque_attente = dossier / "PHOTO-A-FOURNIR.txt"  # empêche la programmation tant qu'une photo manque
        if any(trouver(c) is None for c in chemins):
            marque_attente.write_text("Au moins un visuel utilise un cadre « photo à fournir ».\n", encoding="utf-8")
        elif marque_attente.exists():
            marque_attente.unlink()

    for r in rows:
        if not r["Format"].startswith("Story"):
            continue
        j, mo, a = r["Date"].split("/")
        date = f"{a}-{mo}-{j}"
        sujet, chemins_post = posts_du_jour.get(date, (slug(r["Thème"]), []))
        heures = [h.strip() for h in r["Heure"].split("·")]
        desc = re.sub(r"^À fournir\s*:\s*", "", r["Photo / vidéo"])
        dossier = base_story
        for n, consigne, txt in ecrans_story(r["Légende"]):
            base = dossier / f"{date}-{sujet}-{n}"
            heure = heures[n - 1] if n - 1 < len(heures) else heures[-1]
            infos = [f"Story {n} · {r['Jour']} {j}/{mo} à {heure}", "", f"Consigne : {consigne}"]
            if txt is None:
                infos += ["", "Pas de visuel à créer : cette story se fait directement dans Instagram",
                          "(bouton « Partager » sous la publication ou le réel du jour)."]
            else:
                photo_story = f"photos/{marque}/stories/{date}-{n}.jpg"
                explicite = re.match(r"(photos/\S+?\.(?:jpe?g|png|webp|heic))", desc, re.I)  # photo précise indiquée
                photo = ((trouver(explicite.group(1)) if explicite else None) or trouver(photo_story)
                         or next((p for p in map(trouver, chemins_post) if p), None))
                img, attente = fond(STORY, photo, photo_story, desc)
                mention = EVIN if "Évin" in consigne else None
                enregistrer(carte_story(img, txt, mention), base.with_suffix(".jpg"))
                bilan["stories"] += 1
                bilan["attente"] += attente
                infos += ["", f"Texte sur le visuel : {txt}"]
                quoi = a_ajouter(consigne)
                if quoi:
                    infos += [f"À ajouter dans Instagram : {quoi}"]
            infos += ["", f"Hashtags : {r['Hashtags']}", "Appel à l'action : " + r["Appel à l'action"]]
            if r["À valider"]:
                infos += [f"À valider : {r['À valider']}"]
            base.parent.mkdir(parents=True, exist_ok=True)
            base.with_suffix(".txt").write_text("\n".join(infos) + "\n", encoding="utf-8")

    print(f"{bilan['posts']} visuels de posts, {bilan['stories']} visuels de stories "
          f"({bilan['attente']} en attente de photo).")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Génère les visuels des posts et des stories d'un fichier CSV.")
    ap.add_argument("csv", nargs="?", default="calendriers/da-laura-2026-12.csv")
    ap.add_argument("--marque", help="nom de la marque (sinon déduit du nom du CSV <marque>-AAAA-MM.csv)")
    ap.add_argument("--sortie", help="dossier de sortie (ex. propositions/2026-11-30)")
    a = ap.parse_args()
    main(a.csv, a.marque, a.sortie)
