---
name: contenu-semaine
description: Propose le contenu Instagram de la semaine pour une marque (3 réels, 5 publications, 7 stories, chacun avec visuel, légende et hashtags), à partir de la fiche marque, des nouvelles photos, de la veille et des statistiques, rangé dans propositions/<date>/ avec un récapitulatif à valider. À utiliser quand l'utilisateur dit « Propose-moi du contenu pour la semaine », « du contenu pour la semaine prochaine », « mes propositions de la semaine » ou lance /contenu-semaine.
---

# Propose-moi du contenu pour la semaine

Objectif : livrer dans `propositions/<lundi>/` **3 réels, 5 publications (posts ou carrousels) et 7 stories**, chacun avec son visuel, sa légende et ses hashtags, plus un récapitulatif `A-VALIDER.md`. Rien n'est publié : l'utilisateur valide d'abord.

Arguments possibles : le nom de la marque (défaut `da-laura` ; s'il existe plusieurs fiches dans `marques/` et qu'aucune n'est précisée, demander laquelle) et une date de lundi (défaut : le lundi qui vient).

## Étape 1 : rassembler le contexte

```
python3 outils/semaine.py <marque> [--lundi AAAA-MM-JJ]
```

Le script crée `propositions/<lundi>/contexte.md`. Lire ensuite, dans cet ordre :

1. **La fiche marque** `marques/<marque>.md`, en entier. Elle fait foi pour le ton, le tutoiement, les emojis, les couleurs, les hashtags, les piliers de contenu et les obligations légales.
2. **Les nouvelles photos** listées dans le contexte. Les regarder (outil Read sur les images) pour savoir ce qu'elles montrent vraiment, puis les utiliser **en priorité**.
3. **La veille** du ou des mois concernés (`veille/<AAAA>-<MM>.md`). Si elle manque, la faire d'abord comme l'exige `CLAUDE.md` (recherche web : tendances, dates, concurrents) et l'enregistrer.
4. **Les statistiques** résumées dans le contexte. Reproduire ce qui marche (formats, thèmes et heures des meilleures publications) et le dire dans le récapitulatif. Sans statistiques, le signaler et proposer de lancer `python3 outils/stats_instagram.py <marque>`.
5. **Le calendrier** de la semaine, s'il existe : les propositions **complètent** le calendrier ou proposent des **alternatives**, sans le recopier.

## Étape 2 : écrire `propositions/<lundi>/propositions.csv`

Même format que les calendriers (séparateur `;`, encodage UTF-8 avec BOM), avec les colonnes :
`Date;Jour;Heure;Format;Thème;Temps fort;Photo / vidéo;Texte visuel;Légende;Hashtags;Appel à l'action;À valider`

- **3 lignes `Réel`**, **5 lignes `Post` ou `Carrousel`** et **7 lignes `Story (séquence)`**, soit une story par jour, du lundi au dimanche.
- Répartir sur la semaine selon la fréquence et les horaires de la fiche, en tenant compte des meilleures heures vues dans les statistiques.
- **Photo / vidéo** :
  - post : `photos/<marque>/…/fichier.jpg — description` ; carrousel : `photos/…/sujet-01.jpg à -04.jpg — description` (fichiers numérotés) ;
  - réel : liste explicite `photos/…/a.jpg + photos/…/b.jpg + photos/…/c.jpg — description` (3 à 7 photos, dans l'ordre du montage) ;
  - story : `photos/…/fichier.jpg — description`, avec une séquence d'**un seul écran** : `1. … texte « Texte affiché »` ;
  - photo manquante : `À fournir : photos/<marque>/<dossier>/<sujet>.jpg — ce qu'il faut photographier`, et le noter dans « À valider ».
- **Texte visuel** : 2 à 6 mots, sans emoji.
- **Légende** : ton et règles de la fiche (pour Da Laura : tutoiement, 2 à 4 emojis, une expression italienne au maximum, mots à éviter, mention loi Évin dès qu'il est question d'alcool).
- **Hashtags** : uniquement ceux de la fiche, dans le nombre et l'ordre qu'elle prévoit.
- Ne jamais inventer un prix, un horaire, un plat ou un événement : utiliser `[à compléter]` et le noter dans « À valider ».
- Concurrents : s'en inspirer pour se distinguer, ne jamais copier leurs contenus.

Vérifier :

```
python3 outils/verifier_contenus.py propositions/<lundi>/propositions.csv --marque <marque> --attendu reels=3,posts=5,stories=7
```

Corriger jusqu'à ce que le script affiche « Tout respecte la fiche marque. »

## Étape 3 : générer les visuels et les vidéos

```
python3 outils/generer_visuels.py propositions/<lundi>/propositions.csv --marque <marque> --sortie propositions/<lundi>
python3 outils/generer_reels.py   propositions/<lundi>/propositions.csv --marque <marque> --sortie propositions/<lundi>
```

Les réels prennent environ une minute chacun : lancer la commande en arrière-plan et attendre la fin. Résultat :
`propositions/<lundi>/publications/`, `stories/` et `reels/`, chaque visuel étant accompagné de sa légende (`.txt`).

Ouvrir un visuel de chaque type pour contrôler le rendu.

## Étape 4 : écrire `propositions/<lundi>/A-VALIDER.md`

En français, simple et lisible sur téléphone :

1. Titre : `Propositions de la semaine du <lundi> au <dimanche>` (marque).
2. **En bref** : 3 à 5 puces, avec ce qui a guidé les choix (nouvelles photos utilisées, top des statistiques, dates de la veille).
3. **Tableau récapitulatif** : `| ☐ | N° | Jour et heure | Format | Sujet | Visuel | Pourquoi |`, numéroté R1-R3 (réels), P1-P5 (publications) et S1-S7 (stories), avec des liens relatifs vers les fichiers.
4. **Détail** de chaque proposition : visuel (lien), légende complète, hashtags, appel à l'action, et ⚠️ « À valider » s'il y a lieu.
5. **Photos à fournir**, s'il y en a.
6. **Comment valider** : « Réponds par exemple : *valide R1, P2, S1 à S7 ; modifie P3 : … ; remplace R2* ». Les éléments validés pourront ensuite être ajoutés au calendrier du mois.

## Étape 5 : terminer

```
python3 outils/semaine.py <marque> --lundi <lundi> --terminer
```

Cela note la date dans `propositions/historique.csv` : les « nouvelles photos » de la prochaine fois seront celles ajoutées après cette date.

Puis committer et pousser `propositions/<lundi>/` et l'historique sur la branche de travail. Répondre à l'utilisateur en quelques lignes : le nombre d'éléments, les 2 ou 3 idées fortes, ce qui reste à fournir ou à valider, et le chemin de `A-VALIDER.md`.
