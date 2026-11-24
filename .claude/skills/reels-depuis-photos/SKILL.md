---
name: reels-depuis-photos
description: Dès que l'utilisatrice envoie des photos ou des vidéos (d'un restaurant, d'un plat, d'un événement…) avec ou sans consigne, ou demande un réel ou une vidéo TikTok, propose et MONTE directement des réels personnalisés : une version Instagram et une version TikTok, à partir de ses fichiers, puis les range dans Google Drive. À utiliser aussi avec « fais-moi un réel », « une vidéo avec ces photos », « quelque chose pour TikTok », /reels-depuis-photos.
---

# Photos ou vidéos reçues → réels Instagram et TikTok prêts à publier

L'utilisatrice veut envoyer ses fichiers et recevoir **des réels montés, personnalisés par plateforme**, sans avoir à le demander deux fois.

## 1. Ranger et regarder les fichiers

- Copier chaque fichier reçu dans `photos/<marque>/{plats,cuisine,ambiance,videos}/` avec un nom parlant, **après l'avoir regardé** (outil Read). Le nom doit correspondre à l'image : vérifier deux fois.
- Si un fichier est identique à une photo déjà rangée, ne pas la dupliquer.
- Vidéos : repérer les plans avec `ffmpeg -i <vidéo> -vf "select='gt(scene,0.25)',showinfo" -f null -` et regarder une planche d'images (par exemple 4 images par seconde) pour savoir ce que montre chaque plan.
- **Écarter** : les plans avec de l'alcool (verre servi, bouteille, personne qui boit : loi Évin), les visages de clients reconnaissables sans accord, les images floues, les captures avec des icônes d'Instagram (les recadrer).

## 2. Écrire deux plans de montage (JSON) dans `outils/reels/`

**Version Instagram** (`<sujet>.json`), 15 à 25 s :
- plans de 1,2 à 2 s, élégants ;
- accroche avec la signature de la marque dès la première image ;
- 3 à 5 textes courts, sobres, chacun calé sur le plan qu'il décrit ;
- carte de fin « Réserve ta table » avec l'adresse et le téléphone.

**Version TikTok** (`<sujet>-tiktok.json`), 10 à 15 s :
- plans de 0,6 à 0,9 s, rythme plus rapide ;
- accroche familière en grand dès la première image (par exemple « POV : … ») ;
- textes plus gros, ton plus direct ;
- carte de fin courte (2 s).

Pour les deux :
- **ouvrir sur le plan le plus appétissant ou le plus en mouvement** ;
- raconter une histoire en trois temps (le geste, puis le plat, puis l'humain), et finir sur la marque ;
- **calculer le début de chaque plan** pour caler les textes (somme des durées) ;
- n'écrire que des affirmations vérifiables : « pâtes faites maison » si les photos le montrent, mais jamais « tout est fait maison ».

Format d'un plan : `{"type": "photo", "source": …, "duree": 1.3, "mouvement": "zoom-avant|zoom-arriere|gauche-droite|droite-gauche", "ampleur": 0.12, "centre": [x, y]}` ou `{"type": "video", "source": …, "debut": 9.8, "fin": 11.6}`.

Légende : celle de la fiche marque (ton, emojis, hashtags uniquement de la fiche). Plus courte et plus directe pour TikTok.

## 3. Monter, puis vérifier soi-même

```
python3 outils/monter_reel.py outils/reels/<sujet>.json
python3 outils/monter_reel.py outils/reels/<sujet>-tiktok.json
```

Les deux montages peuvent tourner en parallèle, en arrière-plan.

Extraire 6 à 8 images clés et les regarder : chaque texte est-il sur le bon plan, lisible, sans mot coupé ? La carte de fin est-elle correcte ? Corriger et remonter si besoin.

## 4. Livrer et ranger

1. Envoyer les deux vidéos avec SendUserFile (`display: render`).
2. Google Drive, dossier **DA Laura**, sous-dossier **01 - Réels** (identifiants dans `CLAUDE.md`) :
   - y déposer la couverture et la légende (en Google Doc) de chaque version ;
   - les vidéos de plus de 3 Mo ne passent pas par le connecteur : le dire une fois et rappeler le geste (dans la conversation : Partager, puis Enregistrer dans Fichiers, puis Drive) ;
   - mettre à jour le document **00 - SOMMAIRE**.
3. Committer et pousser.
4. Réponse courte : ce qui est prêt, la différence entre les deux versions, la musique conseillée, et ce qui reste à confirmer.
