import base64, io, json, sys
from PIL import Image, ImageOps
R='/home/user/Assistant-CM/'
def uri(path, size=(360,480), centering=(0.5,0.5), q=78):
    im=ImageOps.fit(Image.open(R+path).convert('RGB'), size, Image.LANCZOS, centering=centering)
    b=io.BytesIO(); im.save(b,'JPEG',quality=q,optimize=True,progressive=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
P='publications/da-laura/'; RL='reels/da-laura/'; RT='photos/da-laura/compte-instagram/retouchees/'
tiles=[ # newest first
 ('reel', RL+'2026-12-30-merci-2026-couverture.jpg','30 déc.','Réel · Merci pour 2026'),
 ('attente', None,'29 déc.','Carrousel · Le Nouvel An à l\'italienne (photos à venir)'),
 ('post', P+'2026-12-25-lustre-bougies/visuel-01.jpg','25 déc.','Post · Buon Natale'),
 ('reel', RL+'2026-12-23-fetes-da-laura-couverture.jpg','23 déc.','Réel · Pour les fêtes'),
 ('carrousel', P+'2026-12-21-spaghetti-crevettes/visuel-01.jpg','21 déc.','Carrousel · La Vigilia'),
 ('reel', RL+'2026-12-16-pause-douceur-couverture.jpg','16 déc.','Réel · La pause douceur'),
 ('carrousel', P+'2026-12-14-planche-fromages-charcuterie/visuel-01.jpg','14 déc.','Carrousel · Les produits d\'Italie'),
 ('reel', RL+'2026-12-09-geste-du-chef-couverture.jpg','9 déc.','Réel · Le geste du chef'),
 ('carrousel', P+'2026-12-08-ravioli-faconnes-main/visuel-01.jpg','8 déc.','Carrousel · Nos pâtes faites maison'),
 ('post', P+'2026-12-06-ardoise-piatti-del-giorno/visuel-01.jpg','6 déc.','Post · Laura, l\'âme de la maison'),
 ('attente', None,'3 déc.','Post · Nos menus de fêtes (menus à venir)'),
 ('reel', RL+'2026-12-02-decouverte-da-laura-couverture.jpg','2 déc.','Réel · La cucina autentica'),
 ('carrousel', P+'2026-12-01-facade-fiat-500-rouge/visuel-01.jpg','1er déc.','Carrousel · Bienvenue chez Da Laura'),
 ('ancien', RT+'risotto-crevettes.jpg','avant','Publication déjà en ligne'),
 ('ancien', RT+'terrasse-chaises-jaunes.jpg','avant','Publication déjà en ligne'),
 ('ancien', RT+'tiramisu-fraise-2.jpg','avant','Publication déjà en ligne'),
 ('ancien', RT+'pates-poele-flamme.jpg','avant','Publication déjà en ligne'),
 ('ancien', RT+'facade-terrasse.jpg','avant','Publication déjà en ligne'),
]
T=[]
for kind,path,date,lab in tiles:
    c=(0.5,0.42) if kind in('reel',) else (0.5,0.5)
    T.append({'k':kind,'src':uri(path,centering=c) if path else '','d':date,'l':lab})
A='stories/da-laura/a-la-une/'
MOTS=[('Piatti','piatti'),('Menu','menu'),('Ambiance','ambiance'),('La cucina','la-cucina'),('Fêtes','fetes'),('Réserver','reserver')]
H={v:[{'l':l,'src':uri(A+v+'/'+f+'.jpg',(140,140),(0.5,0.5),85)} for l,f in MOTS] for v in ('creme','rouge')}
avatar=uri(RT+'enseigne-murale.jpg',(160,160),(0.5,0.5),85)
tpl=open(sys.argv[1]).read()
html=tpl.replace('__TILES__',json.dumps(T)).replace('__HL__',json.dumps(H)).replace('__AVATAR__',avatar)
open(sys.argv[2],'w').write(html); print(len(html))
