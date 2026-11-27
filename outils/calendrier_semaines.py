"""Calendrier « en cases », une page par semaine (lundi → dimanche) : chaque jour avec sa photo, sa légende complète
et sa story. PDF A3 paysage.   python3 outils/calendrier_semaines.py → calendriers/Calendrier-Da-Laura-decembre-2026-semaines.pdf"""
import base64, csv, datetime, glob, html, io, json, subprocess, tempfile
from collections import Counter
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent
def uri(p, w):
    im = Image.open(p).convert("RGB"); im.thumbnail((w, w * 2)); b = io.BytesIO(); im.save(b, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
rows = {}
for r in csv.DictReader(open(R / "calendriers/da-laura-2026-12.csv", encoding="utf-8-sig"), delimiter=";"):
    j, m, a = r["Date"].split("/"); rows[f"{a}-{m}-{j}"] = r
nb = Counter(r["Format"] for r in rows.values())
assert nb["Post"] + nb["Carrousel"] == 8 and nb["Réel"] == 2, f"Contrat Essentielle non respecté : {nb}"
pubs = {Path(p).name[:10]: p for p in glob.glob(str(R / "publications/da-laura/2026-12-*"))}
prog = dict(json.load(open(R / "stories/da-laura/piatti-modeles/2026-12/programme.json")))
J = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
NOTE = {24: "Fermé le soir", 25: "Fermé", 31: "Ouvert le soir · carte réduite"}
def esc(s): return html.escape(s).replace("\n", "<br>")
def case(dt):
    if dt.month != 12:
        return '<td class="hors"></td>'
    k = dt.isoformat(); d = dt.day
    h = f'<div class="jour">{J[dt.weekday()]} <b>{"1er" if d == 1 else d}</b> déc.</div>'
    if d in NOTE: h += f'<div class="note">{NOTE[d]}</div>'
    if k in rows:
        r = rows[k]; fmt = r["Format"]
        afournir = fmt == "Réel" or Path(pubs.get(k, "/x"), "PHOTO-A-FOURNIR.txt").exists()
        h += f'<div class="tag {fmt.lower()}">{r["Heure"]} · {fmt}</div><div class="titre">{esc(r["Texte visuel"])}</div>'
        if afournir:
            h += f'<div class="vide">{"Réel" if fmt == "Réel" else "Photo ou réel"}<br><small>réalisé par toi</small></div>'
        else:
            imgs = sorted(glob.glob(pubs[k] + "/visuel-*.jpg"))
            h += f'<img class="photo" src="{uri(imgs[0], 420)}">'
            if len(imgs) > 1:
                h += '<div class="mini">' + "".join(f'<img src="{uri(i, 90)}">' for i in imgs[1:]) + "</div>"
        h += f'<div class="leg">{esc(r["Légende"])}<br><span class="tags">{esc(r["Hashtags"])}</span></div>'
    if k in prog:
        h += f'<div class="story"><img src="{uri(R / f"stories/da-laura/piatti-modeles/2026-12/{k}.jpg", 90)}"><div><b>11h00 · Story</b><br>Piatti del giorno<br><small>suggestions à ajouter</small></div></div>'
    return f'<td>{h}</td>'
pages = []
lundi = datetime.date(2026, 11, 30)
for s in range(5):
    jours = [lundi + datetime.timedelta(days=s * 7 + i) for i in range(7)]
    dec = [j for j in jours if j.month == 12]
    titre = f"Semaine {s + 1} · du {dec[0].day} au {dec[-1].day} décembre"
    pages.append(f'<section><h1>Da Laura · {titre}</h1><table><tr>{"".join(f"<th>{J[j.weekday()]}</th>" for j in jours)}</tr><tr>{"".join(case(j) for j in jours)}</tr></table></section>')
doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:A3 landscape;margin:10mm}} body{{font-family:Arial,sans-serif;color:#2b211c;margin:0}}
section{{page-break-after:always}} h1{{font-family:Georgia,serif;color:#8E1D1D;font-weight:normal;font-size:24px;margin:0 0 8px}}
table{{width:100%;border-collapse:separate;border-spacing:6px;table-layout:fixed}} th{{background:#8E1D1D;color:#F1E6D3;padding:6px;font-size:13px;border-radius:4px}}
td{{vertical-align:top;background:#fbf8f2;border:1px solid #e6dccb;border-radius:6px;padding:7px;height:245mm}} td.hors{{background:#f0ece6;border-style:dashed}}
.jour{{font-size:13px;color:#8E1D1D;margin-bottom:3px}} .note{{color:#b00;font-weight:bold;font-size:11px;margin-bottom:4px}}
.tag{{display:inline-block;font-size:10.5px;font-weight:bold;color:#fff;background:#5C6B3C;border-radius:3px;padding:2px 5px;margin:2px 0}} .tag.réel{{background:#B8925A}}
.titre{{font-family:Georgia,serif;color:#8E1D1D;font-size:13.5px;margin:2px 0 5px}}
.photo{{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:4px;display:block}}
.mini{{display:flex;gap:2px;margin-top:2px}} .mini img{{width:19%;aspect-ratio:4/5;object-fit:cover;border-radius:2px}}
.vide{{width:100%;aspect-ratio:4/5;border:2px dashed #8E1D1D;border-radius:4px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#8E1D1D;font-size:13px;text-align:center;background:#F1E6D3}}
.leg{{font-size:9.5px;line-height:1.35;margin-top:5px}} .tags{{color:#5C6B3C}}
.story{{display:flex;gap:6px;align-items:center;margin-top:8px;padding-top:6px;border-top:1px solid #e6dccb;font-size:10.5px}} .story img{{width:34px;height:60px;object-fit:cover;border-radius:3px}}
</style></head><body>{"".join(pages)}</body></html>'''
tmp = Path(tempfile.mkdtemp()) / "s.html"; tmp.write_text(doc, encoding="utf-8")
out = R / "calendriers/Calendrier-Da-Laura-decembre-2026-semaines.pdf"
subprocess.run(["node", "-e", f"const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://{tmp}');await p.pdf({{path:'{out}',format:'A3',landscape:true,printBackground:true}});await b.close();}})()"], check=True)
print(out.relative_to(R), dict(nb))
