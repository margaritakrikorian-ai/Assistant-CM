# Publication automatique sur Instagram (@dalaura.cannes)

Ce guide explique, pas à pas, comment permettre au projet de publier **tout seul** les contenus que Laura a validés. À faire **une seule fois**, en 30 à 45 minutes. Tout se fait depuis l'iPad, dans Safari.

> **Tant que vous n'avez pas fait l'étape 6, rien n'est jamais publié.** Le robot tourne en **mode test** : il affiche ce qu'il publierait, sans rien publier ni modifier.

Les menus de Meta changent souvent de nom ou de place : si un bouton ne correspond pas exactement, cherchez un libellé proche (les noms anglais sont entre parenthèses).

---

## Comment ça marche, en bref

1. Dans le calendrier `calendriers/dalaura-AAAA-MM.csv`, chaque contenu a un **statut** : `à créer` → `validé client` → `programmé` ou `publié`.
2. Toutes les heures, un robot GitHub (« GitHub Actions ») lit le calendrier.
3. Il publie **uniquement** les contenus au statut **`validé client`** dont la date et l'heure sont passées (heure de Paris), depuis moins de 24 heures.
4. Juste après chaque publication, il passe le statut à **`publié`** et note le lien du post dans `calendriers/journal-publications.csv`.

Il ne publie **jamais** :
- un contenu `à créer`, `programmé` ou `publié` ;
- un contenu dont l'heure n'est pas encore arrivée ;
- un visuel provisoire (cadre « photo à fournir ») ou une légende qui contient encore un `[texte à compléter]`.

> ⚠️ **Ne mélangez pas les deux méthodes pour un même contenu.** Si vous programmez un contenu à la main dans Meta Business Suite, il doit passer au statut `programmé`. Le robot l'ignorera alors.

---

## Étape 1 : vérifier les comptes (5 min)

1. **Instagram professionnel** : dans l'application Instagram de Da Laura, allez dans ☰, puis **Paramètres et activité**, puis **Type de compte et outils**. Le compte doit être **professionnel** (« Entreprise » de préférence).
2. **Relié à la page Facebook** de Da Laura : sur Facebook, ouvrez la page Da Laura, puis **Paramètres**, puis **Comptes liés** (*Linked accounts*), puis **Instagram**. @dalaura.cannes doit y apparaître. Sinon, touchez **Connecter le compte**.
3. Votre compte Facebook personnel doit être **administrateur** de la page (Paramètres de la page, puis **Accès à la page**).

## Étape 2 : créer l'« app » sur Meta for Developers (10 min)

L'« app » est simplement la porte d'entrée du robot vers Instagram. Elle reste privée.

1. Allez sur **developers.facebook.com**, touchez **Commencer** (*Get Started*) et connectez-vous avec Facebook. Acceptez les conditions et confirmez votre numéro si on vous le demande.
2. Touchez **Mes apps** (*My Apps*), puis **Créer une app** (*Create App*).
3. Nom : `Publication Da Laura`. E-mail : le vôtre.
4. Cas d'utilisation (*Use case*) : choisissez **« Autre »** (*Other*), puis le type **« Entreprise »** (*Business*).
5. Si on vous propose un **portefeuille business** (*Business portfolio*), choisissez celui de Da Laura s'il existe, sinon passez.
6. Dans le tableau de bord de l'app, section **Ajouter des produits** (*Add products*), trouvez **Instagram** et touchez **Configurer** (*Set up*). Si on vous propose deux versions, prenez **« API avec la connexion Facebook »** (*API setup with Facebook login*).

Laissez l'app en **mode développement** : c'est suffisant, car vous publiez sur un compte que vous administrez vous-même. Pas besoin de « vérification de l'app » (*App Review*).

## Étape 3 : obtenir un premier jeton (10 min)

1. Ouvrez l'**Explorateur de l'API Graph** : **developers.facebook.com/tools/explorer**
2. En haut à droite, **Application Meta** (*Meta App*) : choisissez `Publication Da Laura`.
3. **Utilisateur ou page** (*User or Page*) : choisissez **Obtenir un jeton d'accès utilisateur** (*Get User Access Token*).
4. Dans **Autorisations** (*Permissions*), ajoutez ces 6 autorisations :
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `business_management`
5. Touchez **Générer un jeton d'accès** (*Generate Access Token*). Une fenêtre Facebook s'ouvre : choisissez la **page Da Laura** et le compte **@dalaura.cannes**, puis acceptez.

Ce premier jeton ne dure qu'environ **une heure**. L'étape suivante le rend permanent.

## Étape 4 : obtenir un jeton qui n'expire pas (5 min)

1. Copiez le jeton affiché dans l'Explorateur.
2. Ouvrez le **Débogueur de jeton d'accès** : **developers.facebook.com/tools/debug/accesstoken**
3. Collez le jeton, touchez **Déboguer** (*Debug*), puis tout en bas **Prolonger le jeton d'accès** (*Extend Access Token*). Copiez le nouveau jeton, valable 60 jours.
4. Revenez dans l'**Explorateur**, collez ce jeton de 60 jours dans le champ **Jeton d'accès** (*Access Token*) et, dans la barre de requête, tapez :
   ```
   me/accounts?fields=name,access_token,instagram_business_account{username}
   ```
   puis touchez **Envoyer** (*Submit*).
5. Dans la réponse, sur la ligne de la page **Da Laura**, copiez la valeur de **`access_token`**. C'est un **jeton de page** : il **n'expire pas** tant que vous restez administratrice de la page et que vous ne changez pas votre mot de passe Facebook.

> 🔒 Ce jeton donne le droit de publier au nom de Da Laura : traitez-le comme un mot de passe. **Ne le collez jamais** dans une conversation (même avec l'assistant), dans un e-mail ou dans un fichier du projet.

## Étape 5 : ranger le jeton dans les Secrets GitHub (5 min)

1. Sur **github.com**, ouvrez le dépôt du projet, puis **Settings** (Paramètres, en haut à droite ; sur iPad, touchez **…** si l'onglet n'apparaît pas).
2. Dans le menu de gauche : **Secrets and variables**, puis **Actions**.
3. Onglet **Secrets**, puis **New repository secret** :
   - Name : `INSTAGRAM_TOKEN`
   - Secret : collez le **jeton de page** de l'étape 4
   - Touchez **Add secret**.
4. Onglet **Variables**, puis **New repository variable** :
   - Name : `DRY_RUN`
   - Value : `true`
   - Touchez **Add variable**.

GitHub garde le jeton chiffré : il n'apparaît jamais dans le code ni dans les journaux.

## Étape 6 : tester, puis activer

**Tester (sans risque) :**
1. Sur GitHub, ouvrez l'onglet **Actions**, puis **Publication Instagram Da Laura**, puis **Run workflow**, en laissant **Mode test** sur `true`.
2. Ouvrez l'exécution, puis l'étape **Publier les contenus validés…**. Vous devez lire :
   *« [TEST] Jeton valide : compte Instagram @dalaura.cannes »*, puis la liste de ce qui **serait** publié.

**Activer la publication réelle :**
1. Le robot horaire ne tourne que depuis la **branche principale** (`main`) du dépôt. Demandez à l'assistant de « préparer la fusion dans main » : il crée la demande de fusion, que vous acceptez sur GitHub.
2. Dans **Settings**, puis **Secrets and variables**, puis **Actions**, puis **Variables**, changez `DRY_RUN` en **`false`**.

C'est tout. Pour **tout arrêter** à n'importe quel moment, remettez `DRY_RUN` à `true` : effet immédiat au prochain passage.

---

## Au quotidien

- Laura valide un contenu : dites-le à l'assistant (« Laura a validé les posts du 3 et du 6 »), et il passe le statut à `validé client`. Vous pouvez aussi modifier vous-même la colonne `statut` du fichier CSV sur GitHub (icône crayon).
- Le robot publie à l'heure prévue, à quelques minutes près (il passe à la 17e minute de chaque heure). Un contenu prévu à 18:30 part donc vers 19:17.
- **Limites d'Instagram** : 25 publications par jour au maximum. Le robot en publie au plus 3 par passage.
- **En cas d'échec**, le statut reste `validé client` et le robot réessaie l'heure suivante. GitHub vous envoie un e-mail si une exécution échoue.

## En cas de problème

| Message dans le journal | Que faire |
|---|---|
| « Jeton présent mais refusé » | Le jeton a expiré ou a été révoqué (changement de mot de passe Facebook, par exemple). Refaites les étapes 3 à 5. |
| « Aucun compte Instagram professionnel relié à une page Facebook » | Refaites l'étape 1 (liaison page et Instagram), puis l'étape 3 en cochant bien la page et le compte. |
| « Bloqué : visuel provisoire » ou « texte entre crochets » | Le contenu n'est pas fini : il faut la vraie photo ou compléter la légende. |
| « Non publié car trop en retard » | Le contenu a été validé trop tard. Changez sa date ou son heure dans le calendrier. |
| (code 10 ou 200) permission | Une autorisation manque : refaites l'étape 3 avec les 6 autorisations. |

## Comment le robot publie, pour les curieux

L'API officielle d'Instagram exige que chaque image soit accessible à une adresse web. Le robot dépose donc l'image sur la page Facebook de Da Laura en **photo non publiée** (invisible pour le public), puis donne son adresse à Instagram. Les réels sont envoyés directement (« upload » en plusieurs morceaux).

Fichiers concernés :
- `.github/workflows/publier-instagram.yml` : le déclenchement toutes les heures ;
- `outils/publier_instagram.py` : la publication ;
- `outils/programmation.py` : les règles communes (statuts, légendes, formats).

Documentation officielle de Meta :
- [Instagram Platform – Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)
- [Instagram API with Facebook Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/)
- [Jetons d'accès longue durée](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/)
