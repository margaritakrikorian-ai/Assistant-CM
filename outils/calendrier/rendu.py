"""Mise en forme commune des calendriers éditoriaux (CSV + Markdown)."""
import csv, datetime, sys
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

def rendre(OUT, ANNEE, MOIS, MOIS_NOM, NOM, FEED, STORIES, TEXTES, TEMPS_FORTS, NON_RETENUS, A_VALIDER, P, STORY_TAGS):
    def d(j):
        return datetime.date(ANNEE, MOIS, j)

    rows = []
    for (j, h, f, pil, tf, ph, leg, ht, cta, av) in FEED:
        rows.append(dict(date=d(j), heure=h, format=f, theme=pil, temps_fort=tf, photo=ph,
                         legende=leg, hashtags=ht, cta=cta, a_valider=av, ordre=0, texte=TEXTES[j]))
    for (j, h, ph, pil, leg, cta, av) in STORIES:
        tf = next((r[4] for r in FEED if r[0] == j), "")
        rows.append(dict(date=d(j), heure=h, format="Story (séquence)", theme=pil, temps_fort=tf,
                         photo="À fournir : " + ph, legende=leg, hashtags=STORY_TAGS, cta=cta, a_valider=av, ordre=1, texte=""))
    rows.sort(key=lambda r: (r["date"], r["ordre"]))

    # ---- CSV (séparateur ; et BOM pour Excel en français)
    cols = ["Date", "Jour", "Heure", "Format", "Thème", "Temps fort", "Photo / vidéo", "Texte visuel", "Légende", "Hashtags", "Appel à l'action", "À valider"]
    with open(f"{OUT}/{NOM}.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        for r in rows:
            w.writerow([r["date"].strftime("%d/%m/%Y"), JOURS[r["date"].weekday()], r["heure"], r["format"], r["theme"],
                        r["temps_fort"], r["photo"] if r["ordre"] else "À fournir : " + r["photo"], r["texte"], r["legende"],
                        r["hashtags"], r["cta"], r["a_valider"]])

    # ---- Markdown
    def fr(dt):
        mois = MOIS_NOM
        return f"{JOURS[dt.weekday()]} {dt.day}{'er' if dt.day == 1 else ''} {mois}"

    nb = {"Post": 0, "Carrousel": 0, "Réel": 0}
    for r in FEED:
        nb[r[2]] += 1

    md = []
    md.append(f"# Calendrier éditorial : Da Laura, {MOIS_NOM} {ANNEE}\n")
    md.append(f"> Établi à partir de la fiche [`marques/da-laura.md`](../marques/da-laura.md) et de la veille [`veille/{ANNEE}-{MOIS:02d}.md`](../veille/{ANNEE}-{MOIS:02d}.md). Version tableur : [`{NOM}.csv`]({NOM}.csv).\n")
    md.append("## Vue d'ensemble\n")
    md.append(f"- **Publications :** {nb['Post'] + nb['Carrousel']} ({nb['Post']} posts simples et {nb['Carrousel']} carrousels), conformément au contrat (8 par mois)")
    md.append(f"- **Réels :** {nb['Réel']} (contrat : 2 par mois)")
    md.append("- **Stories :** les 20 stories « Piatti del giorno » du mois (plats du jour, du mardi au samedi), créées chaque semaine à partir des plats envoyés : voir `stories/da-laura/plats-du-jour/`")
    md.append("- **Horaires :** 11h–11h30 avant le déjeuner, 18h–18h30 avant le dîner. Le jeudi et le vendredi en fin de journée pour les réservations du week-end.")
    md.append("")
    md.append("### Temps forts retenus\n")
    md.append("| Date | Temps fort | Ce qu'on en fait |\n|---|---|---|")
    for a, b, c in TEMPS_FORTS:
        md.append(f"| {a} | {b} | {c} |")
    md.append("\n" + NON_RETENUS + "\n")

    md.append("## Calendrier jour par jour\n")
    md.append("| Date | Heure | Format | Thème | Sujet |\n|---|---|---|---|---|")
    for r in FEED:
        sujet = r[6].split("\n")[0]
        md.append(f"| {JOURS[d(r[0]).weekday()][:3]} {d(r[0]).strftime('%d/%m')} | {r[1]} | {r[2]} | {r[3]} | {sujet} |")
    md.append("")

    md.append("## Détail des publications\n")
    cur = None
    for r in rows:
        if r["date"] != cur:
            cur = r["date"]
            tf = r["temps_fort"]
            md.append(f"### {fr(cur)}" + (f" · {tf}" if tf else "") + "\n")
        if r["ordre"] == 0:
            md.append(f"**{r['format']} · {r['heure']}** · *{r['theme']}*\n")
            _ch = r['photo'].split(' — ')[0]
            _ok = all(__import__('os').path.exists(c.strip()) for c in _ch.split('+'))
            md.append(f"- **Photo / vidéo :** {'prête' if _ok else 'à fournir'} : `{_ch}`" + (f" ({r['photo'].split(' — ')[1]})" if " — " in r['photo'] else ""))
            md.append(f"- **Texte sur le visuel :** {r['texte']}")
            md.append("- **Légende :**\n")
            md.append("  \n".join("  > " + l for l in r["legende"].split("\n")))
            md.append("")
            md.append(f"- **Hashtags :** {r['hashtags']}")
            md.append(f"- **Appel à l'action :** {r['cta']}")
        else:
            md.append(f"**Stories · {r['heure']}** · *{r['theme']}*\n")
            md.append(f"- **Photo / vidéo :** {r['photo']}")
            md.append("- **Séquence :**\n")
            md.append("\n".join("  " + l for l in r["legende"].split("\n")))
            md.append("")
            md.append(f"- **Hashtags :** {r['hashtags']}")
            md.append(f"- **Appel à l'action :** {r['cta']}")
        if r["a_valider"]:
            md.append(f"- ⚠️ **À valider :** {r['a_valider']}")
        md.append("")

    md.append("## À valider avant publication\n")
    for item in A_VALIDER:
        md.append(f"- {item}")
    md.append("\n## Photos et vidéos à prévoir\n")
    md.append("Voici la liste des prises de vue à réaliser, à déposer dans les sous-dossiers indiqués :\n")
    md.append("| Fichier | Contenu | Pour le |\n|---|---|---|")
    for r in FEED:
        f, _, c = r[5].partition(" — ")
        md.append(f"| `{f.replace(P, '')}` | {c} | {d(r[0]).strftime('%d/%m')} |")
    md.append("")

    with open(f"{OUT}/{NOM}.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    return len(rows)
