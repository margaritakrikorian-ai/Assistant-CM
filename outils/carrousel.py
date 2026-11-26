"""Carrousel Instagram 4:5 (1080x1350) dans la charte Da Laura.

Usage :
  python3 outils/carrousel.py plan.json dossier_sortie/

plan.json :
{
  "titre": ["La pausa dolce", "nos desserts"],
  "slides": [
    {"src": "couverture.jpg"},                       # 1re slide : reçoit le titre
    {"src": "tiramisu.jpg", "nom": "Tiramisù aux fraises"},
    ...
  ]
}
Photos à leur taille réelle (jamais agrandies au-delà de leur définition), filtre naturel,
nom du plat discret en bas, carte de fin crème ajoutée automatiquement.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charte as c

W, H = 1080, 1350


def _centre(d, y, t, f, col, esp=0):
    if esp:
        ws = [d.textbbox((0, 0), ch, font=f)[2] for ch in t]
        x = (W - (sum(ws) + esp * (len(t) - 1))) / 2
        for ch, w in zip(t, ws):
            d.text((x, y), ch, font=f, fill=col); x += w + esp
    else:
        b = d.textbbox((0, 0), t, font=f)
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y), t, font=f, fill=col)


def _texte_sur_photo(img, dessiner, debut_degrade):
    img = img.convert('RGBA')
    g = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(g)
    for y in range(debut_degrade, H):
        gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(120 * min(1, (y - debut_degrade) / 300))))
    txt = Image.new('RGBA', (W, H)); dessiner(ImageDraw.Draw(txt), c.CREME)
    om = Image.new('RGBA', (W, H)); dessiner(ImageDraw.Draw(om), (0, 0, 0))
    om.putalpha(om.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .8)))
    for calque in (g, om, txt):
        img.alpha_composite(calque)
    return img.convert('RGB')


def slide_photo(src, titre=None, nom=None):
    img = c.filtre(c.recadrer(Image.open(src), W / H))
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    if titre:
        def d(dr, col):
            _centre(dr, 1010, titre[0], c.police('manuscrit', 118), col)
            if len(titre) > 1:
                _centre(dr, 1160, titre[1], c.police('italique', 54), col)
        img = _texte_sur_photo(img, d, 820)
    elif nom:
        def d(dr, col):
            _centre(dr, 1215, nom, c.police('italique', 50), col)
        img = _texte_sur_photo(img, d, 1050)
    return img


def slide_fin():
    im = Image.new('RGB', (W, H), c.CREME); d = ImageDraw.Draw(im); cx = W // 2
    d.polygon([(cx - 60, 300), (cx + 60, 300), (cx, 403)], outline=c.ROUGE, width=3)
    _centre(d, 450, 'DA LAURA', c.police('classique', 118), c.ROUGE, esp=13)
    _centre(d, 600, c.SIGNATURE, c.police('italique', 46), c.BRUN)
    d.line([(cx - 85, 695), (cx + 85, 695)], fill=c.OR_DOUX, width=2)
    _centre(d, 725, 'Réserve ta table', c.police('manuscrit', 90), c.ROUGE)
    _centre(d, 855, c.ADRESSE, c.police('italique', 42), c.BRUN)
    _centre(d, 912, c.COMPTE, c.police('italique', 42), c.BRUN)
    pas = 30
    for y in range(H - 120, H, pas):
        for x in range(0, W, pas):
            d.rectangle([x, y, x + pas, y + pas], fill=c.ROUGE if (x // pas + y // pas) % 2 == 0 else c.CREME)
    return im


def monter(plan, sortie):
    os.makedirs(sortie, exist_ok=True)
    fichiers = []
    for i, s in enumerate(plan['slides']):
        img = slide_photo(s['src'], titre=plan['titre'] if i == 0 else None, nom=s.get('nom'))
        f = os.path.join(sortie, f'{i + 1:02d}.jpg'); img.save(f, quality=95); fichiers.append(f)
    f = os.path.join(sortie, f'{len(fichiers) + 1:02d}.jpg'); slide_fin().save(f, quality=95)
    return fichiers + [f]


if __name__ == '__main__':
    print('\n'.join(monter(json.load(open(sys.argv[1])), sys.argv[2])))
