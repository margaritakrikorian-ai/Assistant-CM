# Charte graphique Da Laura

> La signature visuelle de Da Laura sur Instagram, tirée du restaurant lui-même : l'enseigne, l'ardoise et les nappes en vichy. Tous les visuels (posts, stories, réels) la respectent automatiquement.

## 1. L'identité

| Élément | Dans le restaurant | Sur Instagram |
|---|---|---|
| **Signature** | Enseigne « Da Laura – La cucina autentica », plaque « Specialità italiane – Dal 1992 » | « DA LAURA · la cucina autentica · dal 1992 » en pied de chaque story |
| **Emblème** | Triangle pointe en bas avec la silhouette de Laura | Petit triangle au trait (en attendant le fichier du logo) |
| **Écriture manuscrite** | L'ardoise « Piatti del giorno » écrite à la craie | Police **Caveat** pour les titres (« Piatti del giorno ») |
| **Écriture classique** | Les capitales de l'enseigne | Police **Cormorant Garamond** pour les noms de plats et la signature |
| **Motif** | Nappes et serviettes en vichy | Bandes de vichy rouge et crème (styles Duo et Polaroid) |

## 2. Les couleurs

| Couleur | Code | Usage |
|---|---|---|
| Rouge enseigne | `#8E1D1D` | Titres sur fond crème, prix, losanges séparateurs, vichy |
| Rouge vin | `#7A1F2B` | Posts et réels (fiche marque) |
| Crème | `#F1E6D3` | Fonds papier, textes sur photo |
| Brun chaud | `#4A3428` | Descriptions sur fond crème |
| Or craie | `#F2D98B` | Prix sur photo |
| Vert olive / or doux | `#5C6B3C` / `#B8925A` | Touches discrètes (posts) |

## 3. Le filtre photo (même rendu sur toutes les photos)

Chaque photo envoyée passe par le même filtre (`outils/charte_photo.py`). Depuis le 24 novembre 2026, ce filtre est **naturel** : il respecte le rendu des photos déjà publiées sur le compte (l'ancien filtre, chaud et doré, rendait les photos trop jaunes).

- **couleurs et balance des blancs d'origine** : aucun réchauffement, aucune teinte ajoutée ;
- **contraste doux** : un peu plus de relief, sans écraser les noirs ;
- **couleurs ternes légèrement ravivées** (« vibrance »), les couleurs déjà vives restent telles quelles ;
- **aucun flou** : la netteté de la photo est conservée.

Il est appliqué automatiquement par tous les générateurs. Pour obtenir des copies filtrées à publier telles quelles :
`python3 outils/charte_photo.py photos/da-laura` → `photos/da-laura/charte/`.

Les réglages se trouvent en haut du fichier (`CHARTE = {…}`) : les modifier change le rendu de **toutes** les photos à la fois.

## 4. Les stories « Piatti del giorno » : 4 mises en page qui alternent

| Style | Quand l'utiliser |
|---|---|
| **Suggestions** : photo plein cadre, plats écrits dessus | Le style de base, 2 à 4 plats |
| **Duo** : photo en haut, menu sur papier crème en bas, vichy | Pour changer de rythme ; idéal avec l'enseigne ou la salle |
| **Polaroid** : photo encadrée et inclinée, date manuscrite | Le jeudi, plus chaleureux et « souvenir » |
| **Vedette** : un seul plat, en grand | Le samedi ou pour un plat d'exception (truffe, planche à partager) |

Règles :
- une photo peut revenir, mais **jamais deux jours de suite** et avec un **cadrage différent** (ligne `cadrage:`) ;
- **pas de photo contenant déjà du texte** (ardoise, enseigne) derrière une liste de plats : seulement en Duo ou en Polaroid ;
- format **1080x1920**, zones hautes et basses (250 px) laissées libres pour l'interface d'Instagram ;
- photos d'origine en **pleine résolution** : le script prévient quand une photo est trop petite.

## 5. Le rythme

Contrat Essentielle adapté : **20 stories « Piatti del giorno » par mois**, du mardi au samedi (à confirmer). Les plats sont envoyés une fois par semaine avec leurs jours, puis les images sont livrées prêtes à publier.
