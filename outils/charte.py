"""Charte graphique Da Laura (Cannes) : couleurs, polices, filtre photo et visuels.

Usage :
  python3 outils/charte.py photo  <entrée.jpg> <sortie.jpg> [--format 4:5|9:16]
  python3 outils/charte.py titre  <sortie.png> "Titre manuscrit" "petite phrase"
  python3 outils/charte.py fin    <sortie.png>
"""
import os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
POLICES = os.path.join(ICI, '..', 'charte', 'polices')

# Couleurs (charte graphique Da Laura, Google Drive)
ROUGE = (142, 29, 29)      # #8E1D1D rouge enseigne
ROUGE_VIN = (122, 31, 43)  # #7A1F2B
CREME = (241, 230, 211)    # #F1E6D3
BRUN = (74, 52, 40)        # #4A3428
OR_CRAIE = (242, 217, 139) # #F2D98B
OR_DOUX = (184, 146, 90)   # #B8925A
OLIVE = (92, 107, 60)      # #5C6B3C

W, H = 1080, 1920
SIGNATURE = 'la cucina autentica · dal 1992'
ADRESSE = '8 rue du 24 Août · Cannes'
COMPTE = '@dalaura.cannes'

# Filtre photo naturel : balance des blancs d'origine, contraste doux,
# vibrance légère, aucun réchauffement, aucun flou.
FILTRE = dict(contraste=1.05, saturation=1.06, nettete=1.15)
# Équivalent ffmpeg pour les vidéos
FILTRE_FFMPEG = 'eq=contrast=1.05:saturation=1.06,unsharp=3:3:0.3'


def police(nom, taille):
    fichiers = {'manuscrit': 'Caveat-Medium.ttf',
                'classique': 'CormorantGaramond-Medium.ttf',
                'italique': 'CormorantGaramond-MediumItalic.ttf'}
    return ImageFont.truetype(os.path.join(POLICES, fichiers[nom]), taille)


def filtre(img):
    img = ImageEnhance.Contrast(img.convert('RGB')).enhance(FILTRE['contraste'])
    img = ImageEnhance.Color(img).enhance(FILTRE['saturation'])
    return ImageEnhance.Sharpness(img).enhance(FILTRE['nettete'])


def recadrer(img, ratio):
    w, h = img.size
    if w / h > ratio:
        nw = int(h * ratio); return img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = int(w / ratio); return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def photo(entree, sortie, fmt='4:5'):
    taille = (1080, 1350) if fmt == '4:5' else (1080, 1920)
    img = recadrer(Image.open(entree), taille[0] / taille[1]).resize(taille, Image.LANCZOS)
    filtre(img).save(sortie, quality=95)


def _centre(d, y, texte, f, couleur, espace=0):
    if espace:
        ws = [d.textbbox((0, 0), c, font=f)[2] for c in texte]
        x = (W - (sum(ws) + espace * (len(texte) - 1))) / 2
        for c, w in zip(texte, ws):
            d.text((x, y), c, font=f, fill=couleur); x += w + espace
    else:
        b = d.textbbox((0, 0), texte, font=f)
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y), texte, font=f, fill=couleur)


def titre(sortie, ligne1, ligne2=''):
    """Calque transparent 1080x1920 : titre Caveat + phrase Cormorant, crème, ombre douce."""
    def dessiner(d, c):
        _centre(d, 1180, ligne1, police('manuscrit', 120), c)
        if ligne2:
            _centre(d, 1335, ligne2, police('italique', 58), c)
    txt = Image.new('RGBA', (W, H)); dessiner(ImageDraw.Draw(txt), CREME)
    ombre = Image.new('RGBA', (W, H)); dessiner(ImageDraw.Draw(ombre), (0, 0, 0))
    ombre.putalpha(ombre.split()[3].filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * .8)))
    degrade = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(degrade)
    for y in range(1000, H):
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(110 * min(1, (y - 1000) / 500))))
    out = Image.new('RGBA', (W, H))
    for calque in (degrade, ombre, txt):
        out.alpha_composite(calque)
    out.save(sortie)


def fin(sortie):
    """Carte de fin : fond crème, triangle, DA LAURA, signature, Réserve ta table, vichy."""
    im = Image.new('RGB', (W, H), CREME); d = ImageDraw.Draw(im); cx = W // 2
    d.polygon([(cx - 70, 560), (cx + 70, 560), (cx, 680)], outline=ROUGE, width=3)
    _centre(d, 740, 'DA LAURA', police('classique', 128), ROUGE, espace=14)
    _centre(d, 905, SIGNATURE, police('italique', 50), BRUN)
    d.line([(cx - 90, 1010), (cx + 90, 1010)], fill=OR_DOUX, width=2)
    _centre(d, 1050, 'Réserve ta table', police('manuscrit', 96), ROUGE)
    _centre(d, 1190, ADRESSE, police('italique', 44), BRUN)
    _centre(d, 1250, COMPTE, police('italique', 44), BRUN)
    pas = 30
    for y in range(H - 150, H, pas):
        for x in range(0, W, pas):
            d.rectangle([x, y, x + pas, y + pas], fill=ROUGE if (x // pas + y // pas) % 2 == 0 else CREME)
    im.save(sortie)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'photo':
        photo(a[1], a[2], a[4] if len(a) > 4 and a[3] == '--format' else '4:5')
    elif a[0] == 'titre':
        titre(a[1], a[2], a[3] if len(a) > 3 else '')
    elif a[0] == 'fin':
        fin(a[1])
