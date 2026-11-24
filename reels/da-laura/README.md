# Réels Da Laura : décembre 2026

Chaque réel est livré avec trois fichiers :

- `<date>-<sujet>.mp4` : la vidéo verticale en 1080x1920 et 30 images/s, avec une **piste audio silencieuse** à la place de la musique ;
- `<date>-<sujet>.txt` : la légende et les hashtags, prêts à copier-coller ;
- `<date>-<sujet>-couverture.jpg` : l'image de couverture, à choisir dans Instagram via « Modifier la couverture » puis « Ajouter depuis la pellicule ».

## Ajouter la musique dans Instagram

1. Importez le `.mp4` dans Instagram en tant que réel.
2. Touchez l'icône **Musique ♫** et choisissez un morceau dans la bibliothèque Instagram. Ces morceaux sont libres d'utilisation sur la plateforme.
3. Faites démarrer le morceau au moment le plus entraînant et calez sa durée sur celle du réel.
4. La piste de la vidéo étant silencieuse, laissez le volume de l'« audio original » à 0.

> Si le compte est un compte professionnel, certains titres connus ne sont pas proposés. Dans ce cas, prenez un morceau de la catégorie « Audio libre de droits ».

## Ambiance musicale conseillée (contrat : 2 réels par mois)

| Date | Réel | Ambiance musicale |
|---|---|---|
| Mer 02/12 | Pâtes fraîches, faites main (vos photos) | Mandoline ou guitare acoustique italienne, légère et enjouée |
| Mer 16/12 | La table des fêtes (photos à fournir) | Jazz de Noël instrumental, clochettes discrètes |
| Mer 06/01 | La Befana est passée (photos à fournir) | Tarentelle douce ou musique de conte, enjouée |
| Mer 20/01 | Une forme, une sauce (vos photos) | Mandoline italienne légère |

## Remplacer les plans « photo à fournir »

Chaque plan en attente indique le fichier à déposer, par exemple `photos/da-laura/cuisine/pates-fraiches-01.jpg`. Ajoutez les photos sous ces noms, numérotées dans l'ordre du montage, puis relancez :

```
python3 outils/generer_reels.py calendriers/da-laura-2026-12.csv
```

Vous pouvez ajouter jusqu'à 7 photos par réel. Le script adapte la durée de chaque plan pour que la vidéo dure entre 15 et 30 secondes.
