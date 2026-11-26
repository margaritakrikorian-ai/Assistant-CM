"""Fabrique la table de référence (table ronde en métal patiné de Da Laura, photo _DSC7649), vue de dessus,
agrandie x2, vide, pour y poser les plats. Texture recomposée par petits carreaux pris dans la zone libre."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

RACINE = Path(__file__).resolve().parents[2]
SRC = RACINE / "photos/da-laura/ambiance/table-metal-reference.jpg"


def table(w, h, graine=3):
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    zone = im.crop((int(W * 0.43), int(H * 0.845), int(W * 0.75), int(H * 0.99)))  # métal libre, sans objet
    zone = zone.resize((zone.width * 2, zone.height * 2), Image.LANCZOS)  # « x2 »
    z = np.asarray(zone).astype(np.float32)
    rng = np.random.default_rng(graine)
    B, R = 150, 110  # taille des carreaux, recouvrement
    out = np.zeros((h + B, w + B, 3), np.float32)
    poids = np.zeros((h + B, w + B, 1), np.float32)
    rampe = np.minimum(1, np.minimum(np.arange(B + R) + 1, (B + R) - np.arange(B + R)) / R)
    masque = (rampe[:, None] * rampe[None, :])[..., None]
    for y in range(0, h, B):
        for x in range(0, w, B):
            sy = rng.integers(0, z.shape[0] - B - R)
            sx = rng.integers(0, z.shape[1] - B - R)
            bloc = z[sy:sy + B + R, sx:sx + B + R]
            if rng.random() < 0.5:
                bloc = bloc[:, ::-1]
            out[y:y + B + R, x:x + B + R] += bloc[: out.shape[0] - y, : out.shape[1] - x] * masque[: out.shape[0] - y, : out.shape[1] - x]
            poids[y:y + B + R, x:x + B + R] += masque[: out.shape[0] - y, : out.shape[1] - x]
    out = out[R // 2:R // 2 + h, R // 2:R // 2 + w] / np.maximum(poids[R // 2:R // 2 + h, R // 2:R // 2 + w], 1e-3)
    # égalise la lumière (pas de taches d'ombre), rend le grain d'origine
    flou = np.asarray(Image.fromarray(out.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(120))).astype(np.float32)
    moy = out.reshape(-1, 3).mean(0)
    out = out - flou + moy
    out += rng.normal(0, 3.0, out.shape[:2])[..., None]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


if __name__ == "__main__":
    table(1080, 1920).save(RACINE / "outils/table/table-apercu.jpg", quality=92)
