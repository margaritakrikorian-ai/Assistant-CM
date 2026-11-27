"""Fonds de stories « vierges » : zoom sur un détail d'une photo du shooting, léger flou, légère ombre pour que le texte
ajouté dans Instagram reste lisible. Aucun texte. Flou volontaire, à la demande de l'utilisatrice (27/11/2026).
    python3 outils/fonds_flous.py   → stories/da-laura/fonds-flous/*.jpg (1080x1920)"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from charte_photo import appliquer_charte
R = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
# (photo, zone zoomée en fractions de la photo : gauche, haut, droite, bas)
FONDS = [
    ("terrasse-fauteuils", (0.45, 0.40, 1.00, 1.00)),
    ("salle-banquette-jaune", (0.05, 0.40, 0.65, 0.85)),
    ("table-assiettes-peintes", (0.25, 0.45, 0.85, 1.00)),
    ("epicerie", (0.00, 0.00, 0.55, 0.60)),
    ("nids-spaghetti", (0.10, 0.10, 0.70, 0.90)),
    ("pappardelle-fraiches", (0.15, 0.15, 0.75, 0.95)),
    ("chef-citrons", (0.15, 0.35, 0.85, 0.85)),
    ("mur-rose-cadres", (0.10, 0.10, 0.80, 0.80)),
    ("terrasse-rue", (0.20, 0.50, 0.90, 1.00)),
    ("table-bougie", (0.10, 0.20, 0.80, 0.90)),
    ("cappuccino-coeur", (0.20, 0.25, 0.85, 0.85)),
    ("fusilli-crus", (0.10, 0.10, 0.80, 0.90)),
]
if __name__ == "__main__":
    out = R / "stories/da-laura/fonds-flous"; out.mkdir(parents=True, exist_ok=True)
    for i, (nom, (l, t, r, b)) in enumerate(FONDS, 1):
        im = ImageOps.exif_transpose(Image.open(R / f"photos/da-laura/cannes/{nom}.jpg")).convert("RGB")
        w, h = im.size
        im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
        im = ImageOps.fit(im, (W, H), Image.LANCZOS)
        im = appliquer_charte(im).filter(ImageFilter.GaussianBlur(9))
        im = ImageEnhance.Brightness(im).enhance(0.82)
        im.save(out / f"fond-{i:02d}-{nom}.jpg", quality=92)
    print(len(FONDS))
