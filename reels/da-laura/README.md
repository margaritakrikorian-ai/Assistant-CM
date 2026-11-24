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

## Ambiance musicale conseillée

| Date | Réel | Ambiance musicale |
|---|---|---|
| Mer 02/12 | Pâtes fraîches, faites main | Mandoline ou guitare acoustique italienne, légère et enjouée |
| Sam 05/12 | Samedi soir | Jazz lounge ou swing italien des années 60, feutré |
| Mer 09/12 | Le vrai tiramisu | Piano doux, tempo lent |
| Sam 12/12 | Burrata | Lo-fi chaleureux, minimaliste |
| Mer 16/12 | La table des fêtes | Jazz de Noël instrumental, clochettes discrètes |
| Sam 19/12 | Dans nos cuisines | Rythmé, percussions légères, énergie du service |
| Mer 23/12 | Panettone ou pandoro ? | Chant de Noël italien joyeux, en version instrumentale |
| Sam 26/12 | 2026 en images | Cordes et piano émouvants, montée progressive |
| Mer 30/12 | Réveillon : J-1 | Festif et élégant, swing ou électro-jazz |

## Remplacer les plans « photo à fournir »

Chaque plan en attente indique le fichier à déposer, par exemple `photos/da-laura/cuisine/pates-fraiches-01.jpg`. Ajoutez les photos sous ces noms, numérotées dans l'ordre du montage, puis relancez :

```
python3 outils/generer_reels.py calendriers/da-laura-2026-12.csv
```

Vous pouvez ajouter jusqu'à 7 photos par réel. Le script adapte la durée de chaque plan pour que la vidéo dure entre 15 et 30 secondes.

## Réels de janvier 2027

| Date | Réel | Ambiance musicale |
|---|---|---|
| Sam 02/01 | Le 31 décembre en coulisses | Festif et élégant, swing |
| Mer 06/01 | La Befana est passée | Tarentelle douce ou musique de conte, enjouée |
| Sam 09/01 | Le risotto, de A à Z | Guitare acoustique, rythme posé |
| Mer 13/01 | Une matinée en cuisine | Lo-fi matinal, doux |
| Sam 16/01 | Le feu de nos cuisines | Percussions rythmées, énergie |
| Mer 20/01 | Une forme, une sauce | Mandoline italienne légère |
| Sam 23/01 | Avant… après | Jazz lounge qui monte en intensité |
| Mer 27/01 | Le dessert de saison | Piano doux et lumineux |
| Sam 30/01 | Le son de nos cuisines | **Pas de musique** : garder le son original de la vidéo filmée (ASMR) |
