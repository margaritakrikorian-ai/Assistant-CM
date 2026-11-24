---
name: plats-semaine
description: Crée et livre les stories « Piatti del giorno » de la semaine dès que l'utilisatrice envoie les plats du jour (texte, liste, photo de l'ardoise ou capture d'écran), sans rien lui demander d'autre. À utiliser dès qu'un message contient des plats du jour avec des jours ou des dates (« mardi : ravioli burrata 32 €… », « voici les plats de la semaine », photo d'ardoise), ou avec /plats-semaine.
---

# Plats du jour de la semaine : de la réception à la livraison, sans aller-retour

L'utilisatrice veut envoyer **un seul message par semaine** et recevoir les images prêtes à publier. Faire **toutes** les étapes sans poser de question, sauf blocage réel (voir la fin).

## 1. Comprendre le message

- Sources possibles : texte libre, liste, **photo de l'ardoise** ou capture d'écran (la lire avec l'outil Read sur l'image), message transféré.
- Pour chaque jour, retrouver la **date exacte** : « mardi » désigne le prochain mardi à venir, ou celui de la semaine dont il est question. En cas d'ambiguïté, choisir la semaine qui commence au prochain lundi et l'écrire dans le compte rendu.
- Recopier les plats **fidèlement** : nom, description et prix exactement comme envoyés, avec l'orthographe corrigée (accents, majuscules). Ne jamais inventer de plat, d'ingrédient ou de prix. Pas de prix donné : pas de prix affiché.
- Plats écrits en abrégé (« raviolis burrata 32 ») : `Ravioli maison | burrata | 32 €` est acceptable ; garder l'italien quand il est utilisé.

## 2. Écrire le fichier du mois

Ajouter les jours à `plats-du-jour/da-laura-AAAA-MM.txt` (un fichier par mois, à créer à partir de `plats-du-jour/exemple.txt` s'il n'existe pas). Un bloc par jour :

```
2026-12-01
Ravioli maison | pomodorini freschi e burrata | 32 €
Polpo alla piastra | ratatouille du chef | 34 €
```

Si un jour existe déjà, remplacer son bloc. Ne pas ajouter de ligne `style:` ni `photo:` : la mise en page et la photo sont choisies automatiquement. N'en ajouter que si l'utilisatrice l'a demandé, par exemple « mets la photo de Laura jeudi ».

## 3. Générer

```
python3 outils/plats_du_jour.py plats-du-jour/da-laura-AAAA-MM.txt
```

Si la semaine est à cheval sur deux mois, lancer les deux fichiers.

Ce qui est automatique :
- **mise en page** selon le jour : mardi Suggestions, mercredi Duo, jeudi Polaroid, vendredi Suggestions, Vedette dès qu'il n'y a qu'un plat ;
- **photo** : celle du plat si elle existe, sinon une photo du restaurant, jamais la même trois jours de suite ;
- **charte photo** appliquée ;
- sortie dans `stories/da-laura/plats-du-jour/AAAA-MM/`.

## 4. Vérifier soi-même (ne pas déléguer à l'utilisatrice)

- Ouvrir **chaque** image produite (outil Read) et contrôler : textes lisibles, rien de coupé, photo cohérente avec le plat (une photo de dessert derrière un plat de poisson ne va pas) et pas de doublon visible avec la veille.
- Corriger seul si besoin : forcer une autre photo avec `photo:`, un autre cadrage avec `cadrage: x y zoom`, ou une autre mise en page avec `style:`, puis régénérer le jour concerné.

## 5. Livrer

1. Envoyer **toutes les images de la semaine** avec SendUserFile (`display: render`), dans l'ordre des jours, avec une légende courte (« Stories de la semaine du 1er au 5 décembre, prêtes à publier »).
2. Committer et pousser (`plats-du-jour/` et `stories/da-laura/plats-du-jour/`).
3. Répondre en **3 lignes maximum** : ce qui est prêt, et seulement ce qui mérite son attention (un prix manquant qui semblait prévu, une photo basse résolution réutilisée, un plat sans photo correspondante). Pas de détail technique.

## Seuls cas où poser une question

- Impossible de savoir à quels jours correspondent les plats.
- Un texte illisible sur une photo d'ardoise, qui changerait le nom d'un plat ou un prix.

Dans tous les autres cas, choisir la solution la plus raisonnable, la livrer, et la mentionner en une phrase.
