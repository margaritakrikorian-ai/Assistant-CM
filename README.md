# Assistant Community Manager

Un espace de travail pour préparer les contenus des réseaux sociaux de vos clients et de vos marques : fiches marque, photos, calendriers éditoriaux, publications, stories et réels.

## Structure du projet

```
Assistant-CM/
├── photos/          Les photos que vous ajoutez, rangées par client ou par marque
├── marques/         Une fiche par marque (ton, couleurs, cible, hashtags, logo)
│   └── modele.md    Le modèle de fiche marque à copier
├── veille/          La veille du mois (tendances, dates clés, concurrents) avec sources
├── calendriers/     Les calendriers éditoriaux générés
├── propositions/    Les propositions de la semaine, à valider (une par lundi)
├── stats/           Les statistiques Instagram (export ou script)
├── publications/    Les posts prêts à publier (visuel + légende)
├── stories/         Les stories au format 1080x1920
├── reels/           Les réels en vidéo MP4 verticale
├── outils/          Les scripts (visuels, réels, import Instagram)
├── plats-du-jour/    Les plats du jour du mois (pour les stories « Piatti del giorno »)
└── docs/            Les guides (charte graphique, connexion Instagram…)
```

## En une phrase : « Propose-moi du contenu pour la semaine »

Dites simplement cette phrase à l'assistant, ou tapez `/contenu-semaine`. Il :

1. lit la fiche marque, les **nouvelles photos** (ajoutées depuis la dernière proposition), la **veille** du mois et les **statistiques** Instagram ;
2. propose **3 réels, 5 publications et 7 stories**, chacun avec son visuel, sa légende et ses hashtags ;
3. range le tout dans `propositions/<date du lundi>/`, avec un récapitulatif **`A-VALIDER.md`** à cocher.

Vous répondez ensuite, par exemple : *« valide R1, P2, S1 à S7 ; modifie P3 : … »*.

Pour des propositions fondées sur ce qui marche, récupérez d'abord les statistiques : `python3 outils/stats_instagram.py da-laura`, ou déposez un export de Meta Business Suite dans `stats/da-laura/`.

## Démarrage rapide

### 1. Créer la fiche d'une marque

1. Copiez `marques/modele.md` et renommez la copie avec le nom de la marque, en minuscules et sans espaces : `marques/boulangerie-dupont.md`.
2. Remplissez chaque rubrique : ton, couleurs, cible, hashtags, logo, etc.
3. Ajoutez le logo dans `photos/boulangerie-dupont/logo/` et indiquez son chemin dans la fiche.

Plus la fiche est précise, plus les contenus générés seront fidèles à la marque.

### 2. Ajouter les photos

Créez un dossier par client ou par marque, avec **le même nom que la fiche** :

```
photos/
└── boulangerie-dupont/
    ├── logo/
    │   └── logo.png
    ├── produits/
    ├── equipe/
    └── evenements/
```

Conseils :
- Nommez les fichiers de façon parlante : `croissant-beurre-2026-11.jpg` plutôt que `IMG_4521.jpg`.
- Gardez les originaux en bonne résolution (au moins 1080 px de large).

### 3. Générer un calendrier éditorial

Demandez à l'assistant, par exemple :

> « Crée le calendrier éditorial de décembre pour boulangerie-dupont, 3 posts et 5 stories par semaine. »

Le calendrier est enregistré dans `calendriers/`, sous la forme `<marque>-<annee>-<mois>.md` :

```
calendriers/boulangerie-dupont-2026-12.md
```

Avant chaque calendrier, l'assistant fait une **veille** (tendances Instagram du secteur, dates clés en France, en Italie et à Cannes, analyse de 3 concurrents), résumée avec ses sources dans `veille/<AAAA>-<MM>.md`.

### 4. Préparer les publications

Chaque post a son dossier dans `publications/`, avec son visuel et sa légende :

```
publications/
└── boulangerie-dupont/
    └── 2026-12-05-buche-de-noel/
        ├── visuel-01.jpg     (1080x1350 en portrait ; visuel-02, -03… pour un carrousel)
        └── legende.txt       (légende et hashtags, prêts à copier-coller)
```

### Récupérer les photos de vos publications Instagram

Le script `outils/telecharger_instagram.py` télécharge les photos de **vos** publications Instagram dans `photos/<marque>/instagram/`, via l'API officielle de Meta :

```
python3 outils/telecharger_instagram.py da-laura
```

Il faut d'abord connecter le compte : suivez le guide pas à pas [`docs/connecter-instagram.md`](docs/connecter-instagram.md). Le jeton d'accès se range dans un fichier `.env` qui n'est jamais publié sur GitHub (voir `.env.example`).

### Générer automatiquement les visuels

Le script `outils/generer_visuels.py` crée les visuels des posts et des stories d'un calendrier, aux couleurs et aux polices de la marque (Python et Pillow) :

```
python3 outils/generer_visuels.py calendriers/da-laura-2026-12.csv
```

- Il prend les photos indiquées dans la colonne « Photo / vidéo » du calendrier et ajoute le « Texte visuel » en surimpression.
- Si une photo manque, il crée le visuel avec un cadre « PHOTO À FOURNIR » qui indique le fichier attendu. Déposez la photo à cet endroit (en .jpg, .png ou .webp), puis relancez le script.
- Les photos des stories se déposent dans `photos/<marque>/stories/<AAAA-MM-JJ>-<n>.jpg`. À défaut, le script utilise la photo du post du même jour.
- Les réels (vidéos) ne sont pas générés par ce script.

### Générer automatiquement les réels

Le script `outils/generer_reels.py` crée les réels du calendrier avec ffmpeg : une vidéo MP4 verticale en 1080x1920, de 15 à 30 secondes, avec un zoom lent sur chaque photo, des fondus enchaînés, un titre d'accroche dès la première seconde et une carte de fin aux couleurs de la marque.

```
python3 outils/generer_reels.py calendriers/da-laura-2026-12.csv
```

- Les photos se déposent à côté du fichier indiqué dans le calendrier, numérotées dans l'ordre du montage. Par exemple, pour `photos/da-laura/cuisine/pates-fraiches.mp4` : `pates-fraiches-01.jpg`, `pates-fraiches-02.jpg`…
- La piste audio est silencieuse : la musique s'ajoute dans Instagram. Les ambiances conseillées sont dans `reels/<marque>/README.md`.
- Chaque réel est livré avec sa légende (`.txt`) et une image de couverture (`-couverture.jpg`).

### Stories « Piatti del giorno » (plats du jour)

Le contrat de Da Laura prévoit **20 stories de plats du jour par mois**. Elles sont créées avec `outils/plats_du_jour.py`, dans l'écriture du restaurant : l'ardoise à la craie, l'enseigne rouge sur crème « La cucina autentica · dal 1992 » et le vichy des nappes.

1. Copiez `plats-du-jour/exemple.txt` en `plats-du-jour/da-laura-AAAA-MM.txt`, puis ajoutez les plats de chaque jour (`Nom | description | prix`). Vous pouvez aussi simplement envoyer à l'assistant la photo de l'ardoise ou la liste des plats : il remplit le fichier pour vous.
2. Lancez `python3 outils/plats_du_jour.py plats-du-jour/da-laura-AAAA-MM.txt` (style par défaut `suggestions` : une photo du restaurant en fond, différente chaque jour, avec les suggestions écrites dessus ; autres styles : `--style ardoise`, `enseigne` ou `photo`).
3. Les stories arrivent dans `stories/da-laura/plats-du-jour/` (une image et un `.txt` par jour). Les trois modèles sont dans `stories/da-laura/plats-du-jour/modeles/`.

### 5. Créer les stories

Les stories sont au format vertical **1080x1920 pixels** (ratio 9:16) :

```
stories/
└── boulangerie-dupont/
    ├── 2026-12-05-coulisses-1.jpg
    └── 2026-12-05-coulisses-1.txt   (consigne, texte, stickers à ajouter dans Instagram)
```

Laissez environ 250 px libres en haut et en bas de l'image : c'est là que s'affichent le nom du compte et la barre de réponse.

### 6. Créer les réels

Les réels sont des vidéos **MP4 verticales** en 1080x1920 (9:16) :

```
reels/
└── boulangerie-dupont/
    └── 2026-12-10-fabrication-buche.mp4
```

Recommandations : codec H.264, 30 images par seconde, entre 15 et 90 secondes. Gardez les sous-titres et les textes importants au centre de l'image.

## Conventions de nommage

| Élément | Format | Exemple |
|---|---|---|
| Marque | minuscules, tirets | `boulangerie-dupont` |
| Fiche marque | `marques/<marque>.md` | `marques/boulangerie-dupont.md` |
| Calendrier | `<marque>-<AAAA>-<MM>.md` | `boulangerie-dupont-2026-12.md` |
| Publication | `<AAAA>-<MM>-<JJ>-<sujet>/` | `2026-12-05-buche-de-noel/` |
| Story | `<AAAA>-<MM>-<JJ>-<sujet>-<n>.jpg` | `2026-12-05-coulisses-1.jpg` |
| Réel | `<AAAA>-<MM>-<JJ>-<sujet>.mp4` | `2026-12-10-fabrication-buche.mp4` |

Les dates au format `AAAA-MM-JJ` permettent de trier les fichiers dans l'ordre chronologique.

## Exemples de demandes à l'assistant

- « Voici les nouvelles photos de boulangerie-dupont, range-les dans le bon dossier. »
- « Écris 5 légendes Instagram pour la semaine du 8 décembre en respectant la fiche de la marque. »
- « Transforme la publication du 5 décembre en story 1080x1920. »
- « Propose un réel de 30 secondes à partir des photos de fabrication. »
- « Fais le bilan du calendrier de novembre : ce qui a été publié et ce qui reste à faire. »
