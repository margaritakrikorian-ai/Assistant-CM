# Instructions pour l'assistant community manager

## Règle principale : respecter les fiches marque

Avant de produire **tout contenu** pour une marque (légende, calendrier éditorial, visuel, story, réel, réponse à un commentaire), lire sa fiche dans `marques/<marque>.md` et la respecter strictement :

- le ton, le tutoiement ou le vouvoiement, la quantité d'emojis, les mots à utiliser et à éviter ;
- les couleurs (codes hexadécimaux), les typographies et le style photo pour les visuels, stories et réels ;
- les hashtags (de marque, principaux, secondaires, locaux) et le nombre de hashtags par post ;
- la fréquence de publication et les piliers de contenu pour les calendriers ;
- les dates clés et les remarques (obligations légales, langues…).

Si une information nécessaire est marquée *(à compléter)*, la demander ou le signaler plutôt que de l'inventer.

## Marques actives

- **Da Laura** (restaurant italien, Cannes) : `marques/da-laura.md`

## Formats et rangement

- Photos : `photos/<marque>/`
- Calendriers : `calendriers/<marque>-<AAAA>-<MM>.md`
- Publications : `publications/<marque>/<AAAA>-<MM>-<JJ>-<sujet>/` (`visuel-01.jpg`… + `legende.txt`)
- Stories : `stories/<marque>/<AAAA>-<MM>-<JJ>-<sujet>-<n>.jpg` + `.txt`, en 1080x1920
- Réels : `reels/<marque>/`, en MP4 vertical 1080x1920 (H.264, 30 images/s)

Tout le contenu est rédigé en français, sauf indication contraire de la fiche marque.

Visuels des posts (1080x1350) et des stories : générés avec `python3 outils/generer_visuels.py calendriers/<calendrier>.csv` (Pillow, polices dans `outils/polices/`).
Réels (MP4 1080x1920, 15 à 30 s, piste audio silencieuse pour la musique ajoutée dans Instagram) : générés avec `python3 outils/generer_reels.py calendriers/<calendrier>.csv` (ffmpeg).
