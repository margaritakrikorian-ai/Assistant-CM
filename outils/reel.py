"""Monte un Reel 9:16 dans la charte Da Laura à partir de photos et de vidéos.

Usage :
  python3 outils/reel.py plan.json sortie.mp4

plan.json :
{
  "titre": ["La pausa dolce", "une douceur pour finir"],
  "plans": [
    {"src": "photo.jpg", "d": 3.2},
    {"src": "video.mov", "d": 2.2, "debut": 0.5},
    ...
  ]
}
Le titre s'affiche sur le premier plan, la carte de fin est ajoutée automatiquement.
Zoom lent alterné (avant / arrière), fondus de 0,45 s, filtre naturel de la charte, sans musique
(la musique s'ajoute dans Instagram ou TikTok).
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charte

FPS, FONDU = 30, 0.45


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def plan(src, d, sortie, zoom_avant, calque=None, debut=0.0, fin=False):
    n = round(d * FPS)
    z = f'1.0+0.06*on/{n}' if zoom_avant else f'1.06-0.06*on/{n}'
    zp = f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS}"
    image = src.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    if fin:
        entree = ['-loop', '1', '-framerate', str(FPS), '-t', str(d), '-i', src]
        v = (f"[0:v]scale=1188:2112,zoompan=z='1.04-0.04*on/{n}':x='iw/2-(iw/zoom/2)'"
             f":y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS}")
    elif image:
        entree = ['-loop', '1', '-framerate', str(FPS), '-t', str(d), '-i', src]
        v = (f'[0:v]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,'
             f'{charte.FILTRE_FFMPEG},{zp}')
    else:
        entree = ['-ss', str(debut), '-t', str(d), '-i', src]
        v = f'[0:v]fps={FPS},scale=1188:2112:force_original_aspect_ratio=increase,crop=1188:2112,{charte.FILTRE_FFMPEG},{zp}'
    if calque:
        entree += ['-loop', '1', '-framerate', str(FPS), '-t', str(d), '-i', calque]
        fc = (f'{v},format=yuv420p[b];[1:v]format=rgba,fade=in:st=0.25:d=0.6:alpha=1[o];'
              f'[b][o]overlay=0:0,format=yuv420p,setsar=1[v]')
    else:
        fc = f'{v},format=yuv420p,setsar=1[v]'
    ffmpeg(*entree, '-filter_complex', fc, '-map', '[v]', '-frames:v', str(n),
           '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-an', sortie)


def monter(config, sortie):
    tmp = tempfile.mkdtemp()
    calque = os.path.join(tmp, 'titre.png'); charte.titre(calque, *config['titre'])
    carte = os.path.join(tmp, 'fin.png'); charte.fin(carte)
    fichiers, durees = [], []
    plans = config['plans'] + [{'src': carte, 'd': 3.0, 'fin': True}]
    for i, p in enumerate(plans):
        f = os.path.join(tmp, f'{i:02d}.mp4')
        plan(p['src'], p['d'], f, zoom_avant=i % 2 == 0, calque=calque if i == 0 else None,
             debut=p.get('debut', 0.0), fin=p.get('fin', False))
        fichiers.append(f); durees.append(p['d'])
    entrees = sum([['-i', f] for f in fichiers], [])
    fc, prec, t = '', '[0:v]', durees[0]
    for k in range(1, len(fichiers)):
        fc += f'{prec}[{k}:v]xfade=transition=fade:duration={FONDU}:offset={t - FONDU:.3f}[x{k}];'
        prec, t = f'[x{k}]', t + durees[k] - FONDU
    fc += f'anullsrc=r=48000:cl=stereo,atrim=0:{t:.3f}[a]'
    ffmpeg(*entrees, '-filter_complex', fc, '-map', prec, '-map', '[a]', '-c:v', 'libx264',
           '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
           '-movflags', '+faststart', sortie)
    return round(t, 1)


if __name__ == '__main__':
    print(monter(json.load(open(sys.argv[1])), sys.argv[2]), 's')
