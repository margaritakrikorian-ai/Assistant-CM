"""Télécharge les photos de VOS publications Instagram dans photos/<marque>/instagram/.

API officielle : Instagram API with Instagram Login (graph.instagram.com).
Compte requis : Instagram professionnel (Business ou Créateur).

Utilisation (depuis la racine du projet) :
    python3 outils/telecharger_instagram.py da-laura
    python3 outils/telecharger_instagram.py da-laura --limite 50     # 50 dernières publications
    python3 outils/telecharger_instagram.py da-laura --videos        # télécharge aussi les vidéos
    python3 outils/telecharger_instagram.py --rafraichir             # prolonge le jeton de 60 jours

Le jeton d'accès n'est JAMAIS écrit dans le code. Il est lu, dans cet ordre :
  1. la variable d'environnement INSTAGRAM_ACCESS_TOKEN ;
  2. le fichier .env à la racine du projet (ignoré par Git), ligne INSTAGRAM_ACCESS_TOKEN=...
Le jeton est envoyé dans l'en-tête HTTP « Authorization », jamais dans l'adresse.

Aucune bibliothèque à installer : uniquement Python 3.
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER_ENV = RACINE / ".env"
VERSION = os.environ.get("INSTAGRAM_API_VERSION", "v23.0")
API = f"https://graph.instagram.com/{VERSION}"
CHAMPS = ("id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,"
          "children{id,media_type,media_url,thumbnail_url}")


# ---------- jeton ----------
def lire_env():
    valeurs = {}
    if FICHIER_ENV.exists():
        for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#") and "=" in ligne:
                cle, _, val = ligne.partition("=")
                valeurs[cle.strip()] = val.strip().strip('"').strip("'")
    return valeurs


def jeton():
    t = os.environ.get("INSTAGRAM_ACCESS_TOKEN") or lire_env().get("INSTAGRAM_ACCESS_TOKEN")
    if not t or t.startswith("colle-ton-jeton"):
        sys.exit("Jeton introuvable. Copiez .env.example en .env et collez votre jeton après "
                 "INSTAGRAM_ACCESS_TOKEN= (voir docs/connecter-instagram.md).")
    return t


def ecrire_jeton_env(nouveau):
    """Remplace le jeton dans .env sans jamais l'afficher."""
    lignes = FICHIER_ENV.read_text(encoding="utf-8").splitlines() if FICHIER_ENV.exists() else []
    lignes = [l for l in lignes if not l.strip().startswith("INSTAGRAM_ACCESS_TOKEN=")]
    lignes.append(f"INSTAGRAM_ACCESS_TOKEN={nouveau}")
    FICHIER_ENV.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    try:
        os.chmod(FICHIER_ENV, 0o600)
    except OSError:
        pass


# ---------- appels à l'API ----------
def appel(url, params=None, auth=True):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "assistant-cm/1.0"})
    if auth:
        req.add_header("Authorization", f"Bearer {jeton()}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except Exception:
            err = {}
        code, msg = err.get("code"), err.get("message", str(e))
        if code == 190:
            sys.exit("Jeton invalide ou expiré (erreur 190). Générez-en un nouveau dans Meta for Developers "
                     "et mettez à jour .env.")
        if code == 10 or code == 200:
            sys.exit(f"Permission refusée : {msg}\nVérifiez que la permission instagram_business_basic "
                     "est bien accordée.")
        sys.exit(f"Erreur de l'API Instagram ({e.code}) : {msg}")


def publications(limite=None):
    url = f"{API}/me/media"
    params = {"fields": CHAMPS, "limit": 50}
    n = 0
    while url:
        page = appel(url, params)
        params = None  # l'URL « next » contient déjà les paramètres
        for m in page.get("data", []):
            yield m
            n += 1
            if limite and n >= limite:
                return
        url = page.get("paging", {}).get("next")
        if url:  # retirer un éventuel jeton de l'URL de pagination : il passe par l'en-tête
            p = urllib.parse.urlsplit(url)
            q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k != "access_token"]
            url = urllib.parse.urlunsplit(p._replace(query=urllib.parse.urlencode(q)))


def telecharger(url, chemin):
    req = urllib.request.Request(url, headers={"User-Agent": "assistant-cm/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(chemin, "wb") as f:
        while bloc := r.read(1 << 16):
            f.write(bloc)


# ---------- programme principal ----------
def main():
    ap = argparse.ArgumentParser(description="Télécharge les photos de vos publications Instagram.")
    ap.add_argument("marque", nargs="?", help="nom du dossier de la marque, ex. da-laura")
    ap.add_argument("--limite", type=int, help="nombre maximum de publications (les plus récentes)")
    ap.add_argument("--videos", action="store_true", help="télécharger aussi les vidéos (sinon : leur miniature)")
    ap.add_argument("--rafraichir", action="store_true", help="prolonger le jeton de 60 jours (écrit dans .env)")
    a = ap.parse_args()

    if a.rafraichir:
        rep = appel("https://graph.instagram.com/refresh_access_token",
                    {"grant_type": "ig_refresh_token", "access_token": jeton()}, auth=False)
        ecrire_jeton_env(rep["access_token"])
        jours = int(rep.get("expires_in", 0)) // 86400
        print(f"Jeton prolongé et enregistré dans .env (valable environ {jours} jours).")
        return
    if not a.marque:
        ap.error("indiquez la marque, ex. : python3 outils/telecharger_instagram.py da-laura")

    profil = appel(f"{API}/me", {"fields": "username,media_count"})
    print(f"Compte : @{profil.get('username')} ({profil.get('media_count', '?')} publications)")

    dossier = RACINE / "photos" / a.marque / "instagram"
    dossier.mkdir(parents=True, exist_ok=True)
    index = dossier / "index.csv"
    deja = set()
    if index.exists():
        with open(index, encoding="utf-8-sig") as fh:
            deja = {r["Fichier"] for r in csv.DictReader(fh, delimiter=";")}

    lignes, nouveaux, ignores = [], 0, 0
    for m in publications(a.limite):
        date = m.get("timestamp", "")[:10]
        elements = m.get("children", {}).get("data") or [m]
        for k, el in enumerate(elements, 1):
            video = el.get("media_type") == "VIDEO"
            if video and a.videos:
                url, ext = el.get("media_url"), ".mp4"
            else:
                url, ext = (el.get("thumbnail_url") if video else el.get("media_url")), ".jpg"
            if not url:  # ex. contenu protégé par des droits d'auteur : URL non fournie
                ignores += 1
                continue
            suffixe = f"-{k:02d}" if len(elements) > 1 else ""
            nom = f"{date}_{m['id']}{suffixe}{'-miniature' if video and not a.videos else ''}{ext}"
            chemin = dossier / nom
            if not chemin.exists():
                telecharger(url, chemin)
                nouveaux += 1
            if nom not in deja:
                lignes.append({"Date": date, "Fichier": nom, "Type": el.get("media_type"),
                               "Lien": m.get("permalink", ""),
                               "Légende": (m.get("caption") or "").replace("\n", " ")})

    neuf = not index.exists()
    with open(index, "a", newline="", encoding="utf-8-sig" if neuf else "utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Date", "Fichier", "Type", "Lien", "Légende"], delimiter=";")
        if neuf:
            w.writeheader()
        w.writerows(lignes)

    print(f"{nouveaux} fichier(s) téléchargé(s) dans {dossier.relative_to(RACINE)}/"
          + (f", {ignores} ignoré(s) (pas d'URL fournie par Instagram)" if ignores else "") + ".")
    print(f"Liste des photos avec leurs légendes : {index.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
