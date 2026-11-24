# Instructions pour l'assistant community manager

## Règle principale : respecter les fiches marque

Avant de produire **tout contenu** pour une marque (légende, calendrier éditorial, visuel, story, réel, réponse à un commentaire), lire sa fiche dans `marques/<marque>.md` et la respecter strictement :

- le ton, le tutoiement ou le vouvoiement, la quantité d'emojis, les mots à utiliser et à éviter ;
- les couleurs (codes hexadécimaux), les typographies et le style photo pour les visuels, stories et réels ;
- les hashtags (de marque, principaux, secondaires, locaux) et le nombre de hashtags par post ;
- la fréquence de publication et les piliers de contenu pour les calendriers ;
- les dates clés et les remarques (obligations légales, langues…).

Si une information nécessaire est marquée *(à compléter)*, la demander ou le signaler plutôt que de l'inventer.

## Veille avant chaque calendrier éditorial

Avant de créer **chaque** calendrier éditorial, faire une recherche web et la résumer dans `veille/<AAAA>-<MM>.md`, avec les sources (liens) et leur niveau de fiabilité :

1. les tendances Instagram et les formats de réels qui marchent ce mois-ci dans le secteur de la marque (pour Da Laura : restaurant italien) ;
2. les dates clés et les événements du mois en France, dans le pays de la cuisine (Italie) et dans la ville de la marque (Cannes) ;
3. ce que publient 3 concurrents (pour Da Laura : Scalini, Chez Franco Girasole, Tredici), en **analyse seulement**, sans jamais copier leurs contenus.

Le calendrier s'appuie ensuite sur cette veille : il la cite en en-tête, reprend les dates retenues et applique les tendances aux formats. Ne jamais inventer une date ou un événement : ce qui n'est pas sourcé est signalé « à vérifier ».

Les données de chaque calendrier sont dans `outils/calendrier/<marque>_<AAAA>_<MM>.py` (la mise en forme commune est dans `rendu.py`) : `python3 outils/calendrier/<fichier>.py calendriers`.

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

## Instagram et secrets

- Photos des publications Instagram : `python3 outils/telecharger_instagram.py <marque>` (API Instagram Graph, `graph.instagram.com`). Guide : `docs/connecter-instagram.md`.
- Le jeton d'accès n'est **jamais** écrit dans le code ni committé : il se trouve dans `.env` (ignoré par Git) ou dans les secrets de l'environnement. Ne jamais demander à l'utilisateur de le coller dans la conversation : utiliser le formulaire sécurisé.

## Canva

- Serveur MCP officiel de Canva déclaré dans `.mcp.json` (https://mcp.canva.com/mcp). Dossier Canva du mois : « Da Laura – Décembre 2026 ».
- Toujours passer les couleurs, les polices et le ton de la fiche marque dans la description du design (pas de kit de marque Canva configuré).

## Commande « Propose-moi du contenu pour la semaine »

Skill du projet : `.claude/skills/contenu-semaine/SKILL.md` (aussi `/contenu-semaine`). La suivre à la lettre : `outils/semaine.py` (contexte), `propositions.csv`, `outils/verifier_contenus.py`, générateurs avec `--sortie propositions/<lundi>`, `A-VALIDER.md`, puis `--terminer`.

## Contrat et stories « Piatti del giorno » (Da Laura)

- Contrat : formule **Essentielle** adaptée, soit **8 publications, 2 réels et 20 stories « Piatti del giorno » par mois**. Ne pas proposer plus sans le présenter comme une option payante.
- Stories de plats du jour : `python3 outils/plats_du_jour.py plats-du-jour/da-laura-AAAA-MM.txt --style ardoise|enseigne|photo`. Quand l'utilisateur envoie une photo de l'ardoise ou une liste de plats, la retranscrire fidèlement dans le fichier du mois (sans inventer de plat ni de prix) puis générer.
