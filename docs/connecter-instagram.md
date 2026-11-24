# Connecter votre compte Instagram professionnel (API officielle Meta)

Ce guide vous permet d'obtenir un **jeton d'accès** : une sorte de mot de passe temporaire qui autorise le script `outils/telecharger_instagram.py` à lire **vos** publications Instagram. Il faut compter environ 15 minutes, et c'est à faire une seule fois.

> Les menus de Meta changent régulièrement de nom ou de place. Si un bouton ne correspond pas exactement, cherchez un libellé proche. Les noms anglais sont indiqués entre parenthèses.

---

## Avant de commencer

Il vous faut :

1. **Un compte Instagram professionnel** (« Entreprise » ou « Créateur »). Pour le vérifier dans l'application Instagram : votre profil, puis ☰, puis **Paramètres et activité**, puis **Type de compte et outils**. Si vous voyez « Passer à un compte professionnel », c'est que le compte est encore personnel : suivez les étapes, c'est gratuit et immédiat.
2. **Un compte Facebook personnel**, qui sert uniquement à vous connecter à Meta for Developers. Il n'est pas nécessaire de le relier à Instagram.

---

## Étape 1 : créer votre compte développeur

1. Allez sur **https://developers.facebook.com**.
2. Cliquez sur **Commencer** (*Get Started*) en haut à droite et connectez-vous avec Facebook.
3. Acceptez les conditions, puis confirmez votre numéro de téléphone ou votre e-mail si on vous le demande.
4. À la question sur votre métier, choisissez par exemple « Développeur » ou « Autre ». Cela n'a pas d'importance.

## Étape 2 : créer une « app »

L'« app » est simplement la porte d'entrée de votre script vers Instagram. Elle ne sera publiée nulle part.

1. Cliquez sur **Mes apps** (*My Apps*), puis sur **Créer une app** (*Create App*).
2. **Nom de l'app** : par exemple `Assistant CM Da Laura`. **E-mail** : le vôtre.
3. **Cas d'utilisation** (*Use case*) : choisissez **« Gérer les messages et le contenu sur Instagram »** (*Manage messaging & content on Instagram*).
4. Si l'on vous propose de relier un **portefeuille business** (*Business portfolio*), vous pouvez choisir « Je ne veux pas en connecter pour le moment ».
5. Cliquez sur **Créer l'app**. Meta peut redemander votre mot de passe Facebook.

## Étape 3 : ouvrir la configuration de l'API Instagram

1. Dans le tableau de bord de l'app, menu de gauche : **Cas d'utilisation** (*Use cases*), puis **Personnaliser** (*Customize*) à côté du cas d'utilisation Instagram.
2. Ouvrez **Configuration de l'API avec la connexion Instagram** (*API setup with Instagram login*).
3. Vérifiez dans **Autorisations** (*Permissions*) que **`instagram_business_basic`** est présente. C'est la seule dont le script a besoin : elle permet de lire votre profil et vos publications.

## Étape 4 (si Meta le demande) : vous déclarer testeur

Tant que l'app est en « mode développement », elle ne fonctionne qu'avec les comptes qui y ont un rôle. Cela suffit amplement, puisque vous n'utilisez que **votre** compte. Il n'y a pas besoin de « vérification de l'app » (*App Review*).

1. Menu de gauche : **Rôles de l'app** (*App roles*), puis **Rôles**, puis **Ajouter des personnes** (*Add People*), puis **Testeur Instagram** (*Instagram Tester*). Saisissez le nom de votre compte Instagram.
2. Sur Instagram, acceptez l'invitation. Depuis un navigateur sur **instagram.com** : **Paramètres**, puis **Apps et sites web** (*Apps and websites*), puis **Invitations de testeur** (*Tester invites*), puis **Accepter**.

## Étape 5 : générer le jeton d'accès

1. Revenez sur **Configuration de l'API avec la connexion Instagram**.
2. Dans la section **Générer des tokens d'accès** (*Generate access tokens*), cliquez sur **Ajouter un compte** (*Add account*).
3. Une fenêtre Instagram s'ouvre : connectez-vous au compte de **Da Laura**, puis cliquez sur **Autoriser**.
4. Le compte apparaît dans la liste. Cliquez sur **Générer un token** (*Generate token*), cochez la case de confirmation, puis **copiez** le jeton. C'est une longue suite de caractères qui commence souvent par `IG`.

Ce jeton est valable **60 jours**.

> 🔒 **Ce jeton donne accès à votre compte : traitez-le comme un mot de passe.** Ne l'envoyez par e-mail à personne, ne le publiez nulle part et **ne le collez jamais dans une conversation**, même avec l'assistant.

## Étape 6 : enregistrer le jeton dans le projet

Le jeton ne doit **jamais** se trouver dans le code ni sur GitHub. Il se range dans un fichier `.env`, que Git ignore grâce au fichier `.gitignore`.

**Sur votre ordinateur**, si vous travaillez avec une copie du projet :

1. Dans le dossier du projet, faites une copie de `.env.example` et nommez-la `.env`.
2. Ouvrez `.env` avec un éditeur de texte (Bloc-notes, TextEdit…) et remplacez `colle-ton-jeton-ici` par votre jeton :
   ```
   INSTAGRAM_ACCESS_TOKEN=IGAAxxxxxxxxxxxxxxxxxxxx
   ```
3. Enregistrez. Pour vérifier que le fichier est bien ignoré, lancez `git status` : `.env` ne doit **pas** apparaître dans la liste.

**Dans une session Claude Code en ligne** (claude.ai/code) : vous n'avez pas accès aux fichiers de la session. Demandez à l'assistant d'« enregistrer le jeton Instagram ». Il vous ouvrira un **formulaire sécurisé** dans lequel vous collerez le jeton. Le jeton est alors stocké dans les réglages de votre environnement et ajouté automatiquement aux requêtes envoyées à Instagram. L'assistant ne le voit jamais.

## Étape 7 : télécharger vos photos

Depuis la racine du projet :

```
python3 outils/telecharger_instagram.py da-laura
```

- Les photos arrivent dans `photos/da-laura/instagram/`, nommées `<date>_<identifiant>.jpg`. Un carrousel donne `-01`, `-02`…
- Pour les vidéos et les réels, seule la **miniature** est téléchargée. Ajoutez `--videos` pour récupérer aussi les vidéos en MP4.
- Le fichier `photos/da-laura/instagram/index.csv` donne, pour chaque photo, sa date, son lien et sa légende d'origine.
- Vous pouvez relancer le script quand vous voulez : les photos déjà téléchargées ne sont pas re-téléchargées.
- `--limite 30` ne récupère que les 30 dernières publications.

## Renouveler le jeton (tous les 60 jours)

- **Avec un fichier `.env`** : lancez `python3 outils/telecharger_instagram.py --rafraichir` avant l'expiration. Le jeton est prolongé de 60 jours et mis à jour dans `.env` sans jamais s'afficher à l'écran.
- **Dans une session en ligne**, ou si le jeton a déjà expiré : refaites l'étape 5 pour générer un nouveau jeton, puis remplacez l'ancien.

## En cas de problème

| Message | Cause probable | Solution |
|---|---|---|
| « Jeton introuvable » | Pas de fichier `.env`, ou jeton non collé | Refaire l'étape 6 |
| « Jeton invalide ou expiré (erreur 190) » | Jeton expiré, mal copié ou révoqué | Refaire l'étape 5 |
| « Permission refusée » | `instagram_business_basic` non accordée | Étape 3, puis régénérer le jeton |
| Le compte n'apparaît pas à l'étape 5 | Compte non professionnel, ou invitation de testeur non acceptée | « Avant de commencer » et étape 4 |

## Si le jeton a fuité

1. Sur Instagram : **Paramètres**, puis **Apps et sites web**, puis retirez l'accès de l'app. Le jeton cesse immédiatement de fonctionner.
2. Générez un nouveau jeton (étape 5).

---

Documentation officielle de Meta :
- [Créer une app pour la plateforme Instagram](https://developers.facebook.com/docs/instagram-platform/create-an-instagram-app/)
- [Business Login for Instagram](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login)
- [Vue d'ensemble de la plateforme Instagram](https://developers.facebook.com/docs/instagram-platform/overview/)
