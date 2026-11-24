"""Récupère les statistiques de VOS dernières publications Instagram dans stats/<marque>/<AAAA-MM-JJ>.csv.

Utilisation (depuis la racine du projet) :
    python3 outils/stats_instagram.py da-laura            # 30 dernières publications
    python3 outils/stats_instagram.py da-laura --limite 60

- Avec la permission instagram_business_basic : j'aime et commentaires.
- Avec la permission instagram_business_manage_insights en plus : couverture, enregistrements,
  partages, vues et interactions totales (sinon ces colonnes restent vides).
Le jeton est lu comme dans telecharger_instagram.py (.env ignoré par Git, jamais dans le code).

Sans jeton, vous pouvez aussi déposer un export CSV de Meta Business Suite
(Insights > Contenu > Exporter) dans stats/<marque>/ : l'assistant le lira.
"""
import argparse
import csv
import datetime
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from telecharger_instagram import API, RACINE, appel, jeton, publications  # noqa: E402

METRIQUES = ["reach", "saved", "shares", "views", "total_interactions"]
NOMS = {"reach": "Couverture", "saved": "Enregistrements", "shares": "Partages",
        "views": "Vues", "total_interactions": "Interactions"}


def insights(media_id):
    """Statistiques détaillées ; renvoie {} si la permission manque ou si la métrique n'existe pas pour ce format."""
    res = {}
    for m in METRIQUES:
        url = f"{API}/{media_id}/insights?" + urllib.parse.urlencode({"metric": m})
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {jeton()}",
                                                   "User-Agent": "assistant-cm/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r).get("data", [])
            if data:
                res[m] = data[0].get("values", [{}])[0].get("value", data[0].get("total_value", {}).get("value"))
        except urllib.error.HTTPError:
            continue
    return res


def main():
    ap = argparse.ArgumentParser(description="Statistiques des publications Instagram.")
    ap.add_argument("marque", help="nom du dossier de la marque, ex. da-laura")
    ap.add_argument("--limite", type=int, default=30, help="nombre de publications récentes (défaut : 30)")
    a = ap.parse_args()

    profil = appel(f"{API}/me", {"fields": "username,followers_count,media_count"})
    print(f"Compte : @{profil.get('username')} · {profil.get('followers_count', '?')} abonnés")

    dossier = RACINE / "stats" / a.marque
    dossier.mkdir(parents=True, exist_ok=True)
    sortie = dossier / f"{datetime.date.today().isoformat()}.csv"
    cols = ["Date", "Format", "J'aime", "Commentaires"] + [NOMS[m] for m in METRIQUES] + ["Lien", "Légende"]
    n, avec_insights = 0, 0
    with open(sortie, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(cols)
        for m in publications(a.limite):
            if "like_count" not in m:
                m.update(appel(f"{API}/{m['id']}", {"fields": "like_count,comments_count"}))
            ins = insights(m["id"])
            avec_insights += bool(ins)
            fmt = {"CAROUSEL_ALBUM": "Carrousel", "VIDEO": "Réel / vidéo", "IMAGE": "Post"}.get(m.get("media_type"), "")
            w.writerow([m.get("timestamp", "")[:10], fmt, m.get("like_count", ""), m.get("comments_count", "")]
                       + [ins.get(k, "") for k in METRIQUES]
                       + [m.get("permalink", ""), (m.get("caption") or "").replace("\n", " ")[:200]])
            n += 1
    print(f"{n} publications analysées → {sortie.relative_to(RACINE)}")
    if n and not avec_insights:
        print("Statistiques détaillées indisponibles : ajoutez la permission instagram_business_manage_insights "
              "à votre app Meta puis régénérez le jeton (voir docs/connecter-instagram.md).")


if __name__ == "__main__":
    main()
