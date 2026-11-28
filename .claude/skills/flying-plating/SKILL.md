---
name: flying-plating
description: Crée une photo « flying plating » d'un plat de Da Laura Cannes (assiette qui flotte devant le décor du restaurant, éléments du plat qui volent). Utiliser quand l'utilisatrice tape /flying-plating ou demande un plat qui flotte / qui vole / en lévitation.
---

# Flying plating Da Laura (validé par l'utilisatrice le 28/11/2026, tartare _DSC7697)

## Le prompt (ce qu'elle veut)
« Prends la photo du plat que je t'envoie. Détoure l'assiette avec tout ce qu'il y a dessus
(sans napperon, nappe, couverts ni verres). Fais-la flotter, légèrement penchée, devant le décor
de Da Laura **Cannes** flouté comme avec un objectif pro (façade « DA LAURA · Dal 1992 », chaises
colorées, pavés de la terrasse). Ajoute une ombre douce au sol pour montrer qu'elle est en l'air,
et quelques éléments du plat (feuilles, herbes) qui volent autour, certains légèrement flous.
Rendu naturel et réaliste, format 4:5 (1080x1350). »

## Étapes
1. Récupérer la photo HD du plat (dossier Drive « Photo DA LAURA » ou pièce jointe). Vérifier la netteté.
2. Fond par défaut : photo de la façade/terrasse de Cannes (pièce jointe _DSC7621, enseigne
   « DA LAURA · IL LABO · Dal 1992 »). Ne jamais utiliser un décor de Mougins.
3. Lancer : `python3 outils/flying_plating.py plat.jpg fond.jpg sortie.jpg`
   (dépendances : `pip install "rembg[cpu]" opencv-python-headless`).
4. Vérifier l'aperçu : si l'assiette est coupée (rembg ne garde souvent que la nourriture),
   tracer l'ellipse de l'assiette (cv2.fitEllipse sur des points du bord, + la tranche de
   l'assiette décalée vers le bas) et relancer avec `--masque`.
5. Contrôler qu'aucun élément volant n'a de bord carré ou de halo ; sinon le retirer.
6. Livrer avec : verdict noté sur 10, ce qui trahit le montage (souvent la différence de
   lumière plat / fond), une légende prête à poster, et proposer la version vidéo
   (le plat qui s'envole puis se pose).
