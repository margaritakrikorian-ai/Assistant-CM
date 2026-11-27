"""Calendrier jour par jour en PDF (publication + story), pour l'utilisatrice.
    python3 outils/calendrier_pdf.py   → calendriers/Calendrier-Da-Laura-decembre-2026.pdf"""
import base64, csv, datetime, glob, io, json, subprocess, tempfile
from collections import Counter
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent
def uri(p, w):
    im = Image.open(p).convert("RGB"); im.thumbnail((w, w * 2)); b = io.BytesIO(); im.save(b, "JPEG", quality=78)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
rows = {}
for r in csv.DictReader(open(R / "calendriers/da-laura-2026-12.csv", encoding="utf-8-sig"), delimiter=";"):
    j, m, a = r["Date"].split("/"); rows[f"{a}-{m}-{j}"] = r
nb = Counter(r["Format"] for r in rows.values())
assert nb["Post"] + nb["Carrousel"] == 8 and nb["Réel"] == 2, f"Contrat Essentielle non respecté : {nb}"
pubs = {Path(p).name[:10]: p for p in glob.glob(str(R / "publications/da-laura/2026-12-*"))}
prog = dict(json.load(open(R / "stories/da-laura/piatti-modeles/2026-12/programme.json")))
assert len(prog) == 20
J = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
L = []
for d in range(1, 32):
    dt = datetime.date(2026, 12, d); k = dt.isoformat()
    note = {24: "Fermé le soir", 25: "Fermé toute la journée"}.get(d, "")
    pub = ""
    if k in rows:
        r = rows[k]; leg = r["Légende"].split("\n")[0]
        if r["Format"] == "Réel":
            pub = f'<div class="pub"><div class="ph vide">Réel</div><div><b>{r["Heure"]} · Réel</b><br><span class="t">{r["Texte visuel"]}</span><br><span class="m">Réalisé par toi (Instagram + TikTok)</span></div></div>'
        else:
            n = len(glob.glob(pubs[k] + "/visuel-*.jpg"))
            pub = f'<div class="pub"><img class="ph" src="{uri(pubs[k] + "/visuel-01.jpg", 160)}"><div><b>{r["Heure"]} · {r["Format"]}{" (" + str(n) + " photos)" if n > 1 else ""}</b><br><span class="t">{r["Texte visuel"]}</span><br><span class="m">{leg}</span></div></div>'
    st = ""
    if k in prog:
        st = f'<div class="pub"><img class="ph st" src="{uri(R / f"stories/da-laura/piatti-modeles/2026-12/{k}.jpg", 120)}"><div><b>11h00 · Story</b><br><span class="t">Piatti del giorno</span><br><span class="m">Suggestions du jour à ajouter</span></div></div>'
    cls = ' class="we"' if dt.weekday() in (0, 5, 6) else ""
    L.append(f'<tr{cls}><td class="d"><b>{J[dt.weekday()]}</b><br>{d} déc.{"<br><span class=n>" + note + "</span>" if note else ""}</td><td>{pub or "<span class=r>—</span>"}</td><td>{st or "<span class=r>—</span>"}</td></tr>')
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:A4;margin:14mm 12mm}} body{{font-family:Arial,sans-serif;color:#2b211c;font-size:10.5px}}
h1{{font-family:Georgia,serif;color:#8E1D1D;font-weight:normal;font-size:26px;margin:0 0 2px}} .sous{{color:#7a6a5c;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse}} th{{background:#8E1D1D;color:#F1E6D3;text-align:left;padding:6px;font-size:11px}}
td{{border-bottom:1px solid #e6dccb;padding:5px 6px;vertical-align:middle}} tr{{page-break-inside:avoid}} tr.we td{{background:#faf6ef}}
td.d{{width:72px;color:#8E1D1D}} .pub{{display:flex;gap:8px;align-items:center}} .ph{{width:54px;height:68px;object-fit:cover;border-radius:4px;flex:none}}
.ph.st{{width:40px;height:71px}} .vide{{background:#F1E6D3;color:#8E1D1D;display:flex;align-items:center;justify-content:center;font-size:10px;border:1px dashed #8E1D1D}}
.t{{font-family:Georgia,serif;font-size:12.5px;color:#8E1D1D}} .m{{color:#6b5d50}} .r{{color:#c9bba8}} .n{{color:#b00;font-weight:bold;font-size:9.5px}}
.bilan{{margin-top:12px;color:#5a4c40;line-height:1.6}}</style></head><body>
<h1>Da Laura · Calendrier de décembre 2026</h1>
<div class="sous">Formule Essentielle · jour par jour : publications et stories « Piatti del giorno » · @dalaura.cannes</div>
<table><tr><th>Jour</th><th>Publication</th><th>Story</th></tr>{"".join(L)}</table>
<div class="bilan"><b>Contrat Essentielle :</b> 8 publications (5 carrousels, 3 posts) · 2 réels (9 et 23 décembre, réalisés par toi) · 20 stories « Piatti del giorno » du mardi au samedi à 11h00.<br>
Fermetures : le 24 décembre au soir et le 25 toute la journée (pas de story le 25, remplacée par le mardi 29). À confirmer : ouverture le 26 et le 31.</div></body></html>'''
tmp = Path(tempfile.mkdtemp()) / "c.html"; tmp.write_text(html, encoding="utf-8")
out = R / "calendriers/Calendrier-Da-Laura-decembre-2026.pdf"
subprocess.run(["node", "-e", f"const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://{tmp}');await p.pdf({{path:'{out}',format:'A4',printBackground:true}});await b.close();}})()"], check=True)
print(out.relative_to(R), dict(nb))
