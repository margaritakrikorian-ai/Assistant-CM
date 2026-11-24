"""Publication automatique sur Instagram (@dalaura.cannes) via l'API officielle Instagram Graph.

Lancé toutes les heures par GitHub Actions (.github/workflows/publier-instagram.yml), ou à la main :
    DRY_RUN=true python3 outils/publier_instagram.py

Règles de sécurité (non négociables) :
- seuls les contenus au statut EXACT « validé client » sont publiés (accents et majuscules ignorés) ;
- seulement si leur date et heure (heure de Paris) sont passées, et depuis moins de MAX_RETARD_HEURES (24 h par défaut) ;
- jamais un contenu provisoire (cadre « photo à fournir », texte entre crochets à compléter) ;
- MODE TEST PAR DÉFAUT : tant que DRY_RUN ne vaut pas exactement « false », rien n'est publié ni modifié ;
- le statut passe à « publié » juste après chaque publication réussie (le calendrier est enregistré aussitôt).

Variables d'environnement :
    INSTAGRAM_TOKEN   jeton d'accès (Secret GitHub) — jamais dans le code
    DRY_RUN           « true » (défaut) = mode test ; « false » = publication réelle
    IG_USER_ID        facultatif : identifiant du compte Instagram professionnel (trouvé automatiquement sinon)
    FB_PAGE_ID        facultatif : identifiant de la page Facebook reliée (trouvé automatiquement sinon)
    MAX_RETARD_HEURES facultatif : 24 par défaut
    MAX_PAR_PASSAGE   facultatif : nombre maximum de publications par passage (3 par défaut)
"""
import datetime
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from programmation import (FORMATS, PARIS, RACINE, ecrire, est_valide_client, fichiers,  # noqa: E402
                           fichiers_calendrier, legende_finale, lire, moment, preparer_image,
                           preparer_video, problemes)

VERSION = os.environ.get("GRAPH_VERSION", "v23.0")
GRAPH = f"https://graph.facebook.com/{VERSION}"
DRY_RUN = os.environ.get("DRY_RUN", "true").strip().lower() != "false"
MAX_RETARD = datetime.timedelta(hours=float(os.environ.get("MAX_RETARD_HEURES", "24")))
MAX_PAR_PASSAGE = int(os.environ.get("MAX_PAR_PASSAGE", "3"))
JOURNAL = RACINE / "calendriers" / "journal-publications.csv"


class ErreurAPI(Exception):
    pass


# ---------- appels à l'API Graph (bibliothèque standard uniquement) ----------
def _requete(methode, url, params=None, corps=None, entetes=None, jeton=None):
    params = dict(params or {})
    if jeton:
        params["access_token"] = jeton
    if methode == "GET" and params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        donnees = None
    elif corps is not None:
        donnees = corps
    else:
        donnees = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=donnees, method=methode, headers={"User-Agent": "assistant-cm/1.0", **(entetes or {})})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except Exception:
            err = {}
        raise ErreurAPI(f"{err.get('message', e)} (code {err.get('code', e.code)})") from None


def get(chemin, jeton, **params):
    return _requete("GET", f"{GRAPH}/{chemin}", params, jeton=jeton)


def post(chemin, jeton, **params):
    return _requete("POST", f"{GRAPH}/{chemin}", params, jeton=jeton)


def post_fichier(chemin, jeton, champ, fichier, **params):
    """Envoi multipart (upload d'une photo sur la page Facebook)."""
    limite = uuid.uuid4().hex
    morceaux = []
    for k, v in {**params, "access_token": jeton}.items():
        morceaux.append(f"--{limite}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    morceaux.append(f"--{limite}\r\nContent-Disposition: form-data; name=\"{champ}\"; filename=\"{Path(fichier).name}\"\r\n"
                    "Content-Type: image/jpeg\r\n\r\n".encode() + Path(fichier).read_bytes() + b"\r\n")
    morceaux.append(f"--{limite}--\r\n".encode())
    return _requete("POST", f"{GRAPH}/{chemin}", corps=b"".join(morceaux),
                    entetes={"Content-Type": f"multipart/form-data; boundary={limite}"})


# ---------- comptes ----------
def comptes(jeton):
    """Renvoie (id page Facebook, jeton de page, id Instagram, nom du compte Instagram)."""
    ig_id, page_id = os.environ.get("IG_USER_ID"), os.environ.get("FB_PAGE_ID")
    champs = "id,name,access_token,instagram_business_account{id,username}"
    try:
        pages = get("me/accounts", jeton, fields=champs).get("data", [])  # jeton d'utilisateur
    except ErreurAPI:
        pages = []
    if not pages:  # jeton de page : /me désigne directement la page
        moi = get("me", jeton, fields="id,name,instagram_business_account{id,username}")
        moi["access_token"] = jeton
        pages = [moi]
    for p in pages:
        iga = p.get("instagram_business_account")
        if iga and (not ig_id or iga["id"] == ig_id) and (not page_id or p["id"] == page_id):
            return p["id"], p.get("access_token", jeton), iga["id"], iga.get("username", "?")
    raise ErreurAPI("Aucun compte Instagram professionnel relié à une page Facebook n'est accessible avec ce jeton.")


# ---------- hébergement des médias ----------
def url_image(page_id, jeton_page, fichier):
    """Instagram exige une adresse web publique : on dépose l'image sur la page Facebook
    en photo NON publiée (invisible pour le public) et on récupère son adresse."""
    photo = post_fichier(f"{page_id}/photos", jeton_page, "source", fichier, published="false", temporary="true")
    images = get(photo["id"], jeton_page, fields="images").get("images", [])
    if not images:
        raise ErreurAPI("Impossible d'obtenir l'adresse de l'image déposée sur la page.")
    return max(images, key=lambda i: i.get("width", 0))["source"]


def attendre_conteneur(cid, jeton, minutes=10):
    fin = time.time() + minutes * 60
    while time.time() < fin:
        s = get(cid, jeton, fields="status_code,status")
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise ErreurAPI(f"Traitement refusé par Instagram : {s.get('status')}")
        time.sleep(10)
    raise ErreurAPI("Délai dépassé pendant le traitement du média par Instagram.")


# ---------- publication d'un contenu ----------
def publier(l, page_id, jeton_page, ig_id, dossier_tmp):
    fmt = l["format"].strip().lower()
    fs = fichiers(l)
    if fmt == "reel":
        video = preparer_video(fs[0], dossier_tmp / "reel.mp4")
        c = post(f"{ig_id}/media", jeton_page, media_type="REELS", upload_type="resumable",
                 caption=legende_finale(l), share_to_feed="true")
        taille = video.stat().st_size
        _requete("POST", c["uri"], corps=video.read_bytes(),
                 entetes={"Authorization": f"OAuth {jeton_page}", "offset": "0", "file_size": str(taille)})
        cid = c["id"]
    elif fmt == "story":
        img = preparer_image(fs[0], dossier_tmp / "story.jpg", FORMATS["story"])
        cid = post(f"{ig_id}/media", jeton_page, media_type="STORIES",
                   image_url=url_image(page_id, jeton_page, img))["id"]
    elif len(fs) == 1:
        img = preparer_image(fs[0], dossier_tmp / "visuel.jpg", FORMATS["post"])
        cid = post(f"{ig_id}/media", jeton_page, image_url=url_image(page_id, jeton_page, img),
                   caption=legende_finale(l))["id"]
    else:  # carrousel
        enfants = []
        for i, f in enumerate(fs, 1):
            img = preparer_image(f, dossier_tmp / f"visuel-{i:02d}.jpg", FORMATS["post"])
            enfants.append(post(f"{ig_id}/media", jeton_page, image_url=url_image(page_id, jeton_page, img),
                                is_carousel_item="true")["id"])
        for e in enfants:
            attendre_conteneur(e, jeton_page)
        cid = post(f"{ig_id}/media", jeton_page, media_type="CAROUSEL", children=",".join(enfants),
                   caption=legende_finale(l))["id"]
    attendre_conteneur(cid, jeton_page)
    media = post(f"{ig_id}/media_publish", jeton_page, creation_id=cid)
    return media["id"]


def journaliser(l, media_id, lien):
    neuf = not JOURNAL.exists()
    with open(JOURNAL, "a", encoding="utf-8-sig" if neuf else "utf-8") as fh:
        if neuf:
            fh.write("publié le;date prévue;heure;format;fichier;id instagram;lien\n")
        fh.write(f"{datetime.datetime.now(PARIS):%Y-%m-%d %H:%M};{l['date']};{l['heure']};{l['format']};"
                 f"{l['fichier']};{media_id};{lien}\n")


# ---------- programme principal ----------
def main():
    maintenant = datetime.datetime.now(PARIS)
    print(f"{'MODE TEST (DRY_RUN) : rien ne sera publié' if DRY_RUN else 'MODE RÉEL : publication activée'} · "
          f"{maintenant:%d/%m/%Y %H:%M} (heure de Paris)\n")

    a_publier, a_venir, en_retard, bloques = [], [], [], []
    for cal in fichiers_calendrier():
        for l in lire(cal):
            if not est_valide_client(l):
                continue  # JAMAIS de publication d'un contenu non validé par le client
            quand = moment(l)
            if quand > maintenant:
                a_venir.append(l)
            elif maintenant - quand > MAX_RETARD:
                en_retard.append(l)
            elif problemes(l):
                bloques.append((l, problemes(l)))
            else:
                a_publier.append((cal, l))
    a_publier.sort(key=lambda x: moment(x[1]))

    print(f"À publier maintenant : {len(a_publier)} · À venir (validés) : {len(a_venir)} · "
          f"En retard de plus de {MAX_RETARD.total_seconds() / 3600:.0f} h (non publiés) : {len(en_retard)} · "
          f"Bloqués : {len(bloques)}\n")
    for l in en_retard:
        print(f"⏰ Non publié car trop en retard : {l['date']} {l['heure']} {l['format']} ({l['fichier']})")
    for l, p in bloques:
        print(f"⛔ Bloqué : {l['date']} {l['heure']} {l['format']} : {' ; '.join(p)}")

    jeton = os.environ.get("INSTAGRAM_TOKEN", "").strip()
    if DRY_RUN:
        for _, l in a_publier[:MAX_PAR_PASSAGE]:
            print(f"\n[TEST] Serait publié : {l['date']} {l['heure']} · {l['format']} · {len(fichiers(l))} fichier(s)")
            print("       " + legende_finale(l).replace("\n", "\n       ")[:600])
        if len(a_publier) > MAX_PAR_PASSAGE:
            print(f"\n[TEST] {len(a_publier) - MAX_PAR_PASSAGE} autre(s) contenu(s) seraient publiés au passage suivant.")
        if jeton:
            try:
                _, _, ig_id, nom = comptes(jeton)
                print(f"\n[TEST] Jeton valide : compte Instagram @{nom} (id {ig_id}).")
            except ErreurAPI as e:
                print(f"\n[TEST] ⚠️ Jeton présent mais refusé : {e}")
        else:
            print("\n[TEST] Aucun jeton INSTAGRAM_TOKEN : la vérification du compte est ignorée.")
        print("\nMode test : aucun contenu publié, aucun statut modifié.")
        return

    if not a_publier:
        print("Rien à publier.")
        return
    if not jeton:
        sys.exit("Publication impossible : le Secret INSTAGRAM_TOKEN est vide.")
    page_id, jeton_page, ig_id, nom = comptes(jeton)
    print(f"Compte : @{nom}\n")

    erreurs = 0
    for cal, l in a_publier[:MAX_PAR_PASSAGE]:
        # relecture juste avant de publier : le statut doit TOUJOURS être « validé client »
        lignes = lire(cal)
        cible = next((x for x in lignes if all(x[c] == l[c] for c in ("date", "heure", "format", "fichier"))), None)
        if cible is None or not est_valide_client(cible):
            print(f"↷ Ignoré (statut modifié entre-temps) : {l['date']} {l['format']}")
            continue
        try:
            with tempfile.TemporaryDirectory() as tmp:
                media_id = publier(cible, page_id, jeton_page, ig_id, Path(tmp))
        except (ErreurAPI, OSError, ValueError) as e:
            erreurs += 1
            print(f"✗ Échec : {l['date']} {l['heure']} {l['format']} : {e} (statut inchangé, nouvel essai au prochain passage)")
            continue
        cible["statut"] = "publié"
        ecrire(cal, lignes)  # enregistré tout de suite pour ne jamais publier deux fois
        try:
            lien = get(media_id, jeton_page, fields="permalink").get("permalink", "")
        except ErreurAPI:
            lien = ""
        journaliser(cible, media_id, lien)
        print(f"✓ Publié : {l['date']} {l['heure']} {l['format']} → {lien or media_id}")
    if erreurs:
        sys.exit(f"{erreurs} publication(s) en échec : voir le détail ci-dessus.")


if __name__ == "__main__":
    main()
