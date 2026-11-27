"""Données du calendrier éditorial. Usage : python3 outils/calendrier/<fichier>.py calendriers"""
import csv, datetime, sys

BASE = "calendriers/da-laura-2026-12"
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
P = "photos/da-laura/"
STORY_TAGS = "#DaLaura + sticker localisation « Cannes »"
EVIN = "L'abus d'alcool est dangereux pour la santé, à consommer avec modération."

# (jour, heure, format, pilier, temps_fort, photo, legende, hashtags, cta, a_valider)
FEED = [
 (1, "18h30", "Carrousel", "L'ambiance", "Début du mois des fêtes",
  P+"ambiance/salle-noel-01.jpg à -05.jpg — salle décorée pour Noël, bougies, détails déco",
  "Décembre s'installe chez Da Laura. ✨\nLes bougies sont allumées, la salle s'habille pour les fêtes et la cuisine prépare déjà les recettes de Noël à l'italienne.\nTout ce mois-ci, on te fait découvrir nos traditions, nos coulisses et quelques surprises.\nBenvenuti a Natale 🎄\nRéserve ta table via le lien en bio.",
  "#DaLaura #RestaurantItalienCannes #CuisineItalienne #DolceVita #Cannes #FrenchRiviera",
  "Réserve ta table via le lien en bio",
  "Décoration de Noël installée au 1er décembre"),
 (2, "18h30", "Réel", "Le savoir-faire", "",
  P+"cuisine/pates-fraiches.mp4 — farine en fontaine, œufs, pétrissage, laminage, découpe des tagliatelle, assiette finale (20-30 s)",
  "Farine, œufs, patience. Et les mêmes gestes, répétés chaque matin. 🍝\nNos pâtes fraîches sont tirées à la main en cuisine avant le service : c'est ce qui leur donne cette texture tendre et légèrement rugueuse qui retient parfaitement la sauce.\nTu les préfères en tagliatelle, en pappardelle ou en ravioli ? Dis-le-nous en commentaire 👇",
  "#DaLaura #PastaFresca #CuisineItalienne #PâtesFraîches #FaitMaison #CannesFood",
  "Dis-nous en commentaire ta forme de pâtes préférée",
  "Formes de pâtes réellement à la carte"),
 (3, "11h30", "Post", "La carte", "Menus de Noël et de la Saint-Sylvestre",
  P+"plats/menu-fetes.jpg — table de fête dressée avec un plat du menu de Noël",
  "Les fêtes approchent, et ta table chez Da Laura aussi. 🎄\nPour Noël et la Saint-Sylvestre, la cuisine prépare des menus de fête à l'italienne : [détail des menus et prix à compléter].\nLes places sont limitées pour ces soirées : réserve dès maintenant via le lien en bio. ✨",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #RestaurantCannes #DolceVita #Cannes #FrenchRiviera",
  "Réserve ta soirée de fête via le lien en bio",
  "Ouverture les 24, 25 et 31 décembre ; contenu et prix des menus"),
 (4, "18h30", "Carrousel", "La carte", "",
  P+"plats/carte-hiver-01.jpg à -06.jpg — 4 à 6 plats d'hiver (risotto, ragù, pâtes fraîches, dessert)",
  "Quand les soirées fraîchissent sur la Croisette, la cuisine italienne sait réchauffer. 🌿\nRisotto crémeux, ragù mijoté pendant des heures, pâtes fraîches et desserts gourmands : découvre en images les plats de notre carte d'hiver.\nGlisse jusqu'à la fin pour voir notre coup de cœur du moment. ✨\nTa table du week-end t'attend, réserve via le lien en bio.",
  "#DaLaura #CuisineItalienne #ItalianFood #Risotto #FaitMaison #CannesFood #CôteDAzur",
  "Réserve ta table du week-end via le lien en bio",
  "Plats réellement à la carte d'hiver"),
 (5, "18h00", "Réel", "L'ambiance", "",
  P+"ambiance/samedi-soir.mp4 — bougies qu'on allume, salle qui se remplit, assiettes qui sortent (15-20 s)",
  "Samedi soir chez Da Laura. 🕯️\nLes bougies s'allument, les premières assiettes sortent de la cuisine et la salle se remplit doucement de conversations et de rires.\nCe soir, c'est peut-être ta table. Ci vediamo stasera ✨\nRéserve via le lien en bio.",
  "#DaLaura #DaLauraCannes #RestaurantCannes #DolceVita #FoodLover #Cannes #FrenchRiviera",
  "Réserve via le lien en bio",
  "Accord des clients reconnaissables à l'image"),
 (6, "11h30", "Post", "L'équipe et Laura", "",
  P+"equipe/laura-portrait.jpg — Laura en cuisine, lumière chaude",
  "Derrière Da Laura, il y a Laura. ❤️\n[Une à deux phrases sur son histoire : sa région d'origine, ce qui l'a amenée à Cannes.]\nSa conviction : une belle cuisine italienne commence par de beaux produits et se termine autour d'une table partagée.\nEt toi, qu'aimerais-tu lui demander ? Pose ta question en commentaire, elle te répondra en story cette semaine. 👇",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #ItalianRestaurant #FaitMaison #CannesRestaurant",
  "Pose ta question à Laura en commentaire",
  "Histoire de Laura (à ajouter dans la fiche marque)"),
 (7, "18h30", "Post", "La carte", "Repas de fin d'année",
  P+"ambiance/grande-tablee.jpg — grande table dressée pour un groupe",
  "Repas d'équipe, dîner entre amis, retrouvailles en famille : décembre, c'est la saison des grandes tablées. 🍝\nChez Da Laura, on s'occupe de tout : une table dressée avec soin, des plats à partager à l'italienne et un service attentif du début à la fin.\nPour ton repas de fin d'année, écris-nous en message privé : on te prépare une proposition sur mesure. ✨",
  "#DaLaura #RestaurantCannes #RestaurantItalienCannes #ItalianRestaurant #Cannes #AlpesMaritimes",
  "Écris-nous en message privé pour ton repas de groupe",
  "Capacité d'accueil, offre groupes et privatisation"),
 (8, "11h30", "Carrousel", "Cannes et la dolce vita", "Immacolata (8 décembre)",
  P+"ambiance/sapin-01.jpg à -04.jpg — sapin, crèche et détails de décoration du restaurant",
  "Le 8 décembre, en Italie, on fête l'Immacolata… et c'est le jour où l'on décore le sapin et installe la crèche. 🎄\nUne tradition que l'on perpétue chez Da Laura : à partir d'aujourd'hui, la maison est officiellement en mode Natale.\nGlisse pour découvrir notre décoration, et dis-nous en commentaire : chez toi, le sapin est déjà prêt ? ✨",
  "#DaLaura #CuisineItalienne #ItalianFood #DolceVita #Cannes #CôteDAzur",
  "Dis-nous en commentaire si ton sapin est prêt",
  ""),
 (9, "18h30", "Réel", "Le savoir-faire", "",
  P+"cuisine/tiramisu.mp4 — mascarpone, café, biscuits trempés, couches, cacao saupoudré, première cuillère (20-30 s)",
  "Le secret d'un vrai tiramisu ? Du mascarpone, un café bien serré, de la patience… et une nuit de repos au frais. ☕\nChez Da Laura, il est préparé en cuisine, comme à la maison.\nEnregistre ce réel pour ton prochain dessert, ou viens le goûter directement à table. 🤌",
  "#DaLaura #Tiramisu #FaitMaison #CuisineItalienne #ItalianFood #CannesFood",
  "Enregistre ce réel",
  "Tiramisu à la carte ; si la recette contient un alcool, ne pas montrer la bouteille"),
 (10, "18h30", "Post", "La carte", "Idées cadeaux de Noël",
  P+"plats/carte-cadeau.jpg — carte cadeau posée sur une table, ruban, bougie",
  "Et si cette année, tu offrais un moment plutôt qu'un objet ? 🎁\nLa carte cadeau Da Laura, c'est un dîner à l'italienne à partager : des pâtes fraîches, un dessert maison et une soirée à Cannes dont on se souvient.\nÉcris-nous en message privé pour la commander. ✨",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #DolceVita #CannesRestaurant #FrenchRiviera",
  "Écris-nous en message privé pour commander ta carte cadeau",
  "Existence de la carte cadeau, montants, achat en ligne ou sur place"),
 (11, "18h30", "Post", "La carte", "",
  P+"plats/accord-mets-vins.jpg — plat de ragù et verre de vin rouge, visuel sobre",
  "Un beau plat italien mérite un vin à sa hauteur. 🍷\nAvec un ragù mijoté, on aime un rouge du Piémont ou de Toscane aux tanins souples ; avec un risotto aux champignons, un blanc sec et minéral du nord de l'Italie.\nDemande conseil à notre équipe en salle : elle te guidera vers le bon accord. ✨\n" + EVIN,
  "#DaLaura #VinoItaliano #CuisineItalienne #ItalianFood #RestaurantCannes #Cannes",
  "Demande conseil à notre équipe en salle",
  "Vins réellement à la carte ; mention loi Évin à garder (déjà dans la légende)"),
 (12, "18h00", "Réel", "La carte", "",
  P+"plats/burrata.mp4 — burrata coupée au ralenti, filet d'huile d'olive, basilic (10-15 s)",
  "Ce moment où la burrata s'ouvre. 🤍\nCrémeuse à cœur, servie avec une huile d'olive italienne, quelques tomates et du basilic frais : quand les produits sont bons, la simplicité suffit.\nIdentifie la personne avec qui tu la partagerais… ou pas. 😉",
  "#DaLaura #Burrata #Antipasti #ItalianFood #CuisineItalienne #CannesFood #CôteDAzur",
  "Identifie la personne avec qui tu la partagerais",
  "Burrata à la carte"),
 (13, "11h00", "Post", "La communauté", "",
  P+"ambiance/dejeuner-famille.jpg — grands plats au centre de la table, mains qui se servent",
  "Le dimanche, en Italie, c'est sacré : on se retrouve en famille, on prend le temps et on partage de grands plats au centre de la table. 🍝\nC'est cet esprit que l'on aime retrouver chez Da Laura, avec les petits comme avec les grands.\nTa table t'attend ce midi : réserve via le lien en bio. ❤️",
  "#DaLaura #RestaurantItalienCannes #CuisineItalienne #FoodLover #Cannes #AlpesMaritimes",
  "Réserve via le lien en bio",
  "Ouverture le dimanche midi"),
 (14, "18h30", "Carrousel", "Le savoir-faire", "",
  P+"plats/produits-italie-01.jpg à -05.jpg — parmesan, huile d'olive, farine, mozzarella/burrata, chacun en gros plan",
  "D'où viennent nos produits ? On t'emmène en Italie. 🇮🇹\nParmigiano Reggiano affiné, huile d'olive extra vierge, farine pour nos pâtes fraîches, mozzarella et burrata : chaque ingrédient est choisi pour son origine et son goût.\nGlisse pour découvrir leur histoire, région par région. 🌿\nEnregistre ce post pour ta prochaine envie d'Italie.",
  "#DaLaura #CuisineItalienne #ItalianFood #FaitMaison #Antipasti #CannesFood",
  "Enregistre ce post",
  "Produits, fournisseurs et régions d'origine exacts"),
 (15, "11h30", "Post", "La communauté", "",
  P+"plats/avis-client.jpg — plat signature + citation de l'avis en surimpression",
  "Il y a des messages qui font notre journée. ✨\n« [Citation d'un avis client récent, avec son accord.] »\nMerci à toutes celles et ceux qui partagent leur soirée chez Da Laura : c'est grâce à vous que la maison vit.\nTu es venu récemment ? Identifie-nous dans tes stories, on adore les republier. 📸",
  "#DaLaura #RestaurantCannes #CuisineItalienne #FoodLover #CannesFood #Cannes",
  "Identifie-nous dans tes stories",
  "Avis réel et accord de son auteur"),
 (16, "18h30", "Réel", "L'ambiance", "Noël",
  P+"ambiance/table-fete.mp4 — dressage d'une table de fête en accéléré (15-20 s)",
  "Nappe blanche, couverts alignés, bougies et branches d'olivier : on dresse la table des fêtes. 🕯️\nChaque détail compte pour que ta soirée commence dès que tu passes la porte.\nDis-nous en commentaire ce qui fait, pour toi, une belle table de fête. 👇",
  "#DaLaura #RestaurantCannes #DolceVita #ItalianRestaurant #CannesRestaurant #CôteDAzur",
  "Dis-nous en commentaire ce qui fait une belle table de fête",
  ""),
 (17, "18h30", "Post", "La communauté", "Jeu-concours de Noël (17 → 19 décembre)",
  P+"plats/jeu-concours.jpg — table pour deux dressée, bougie, carte « À gagner »",
  "Pour fêter Noël avec toi, on t'offre un dîner pour deux chez Da Laura. 🎁\nPour participer :\n1. Abonne-toi à @[compte Instagram]\n2. Aime ce post\n3. Identifie en commentaire la personne avec qui tu viendrais\nFin du jeu le samedi 19 décembre à 23h59, tirage au sort le dimanche 20. Bonne chance ✨\nRèglement en bio. Ce jeu n'est ni organisé ni sponsorisé par Instagram.",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #CuisineItalienne #Cannes #CannesFood",
  "Abonne-toi, aime et identifie la personne avec qui tu viendrais",
  "Dotation (sans boissons alcoolisées), règlement, nom du compte Instagram"),
 (18, "18h30", "Post", "Cannes et la dolce vita", "Illuminations et village de Noël du Palm Beach",
  P+"ambiance/croisette-illuminations.jpg — la Croisette illuminée à la tombée de la nuit",
  "Cannes en décembre a un charme particulier : les illuminations, le village de Noël du Palm Beach sur la Croisette, la mer d'hiver et cette douceur qui donne envie de sortir. ✨\nAprès une balade au bord de l'eau, rien de tel qu'une table chaleureuse et une assiette de pâtes fraîches pour finir la soirée.\nTa soirée cannoise se termine chez nous ? Réserve via le lien en bio. 🍝",
  "#DaLaura #RestaurantCannes #DolceVita #PastaFresca #Cannes #FrenchRiviera #CannesFrance",
  "Réserve via le lien en bio",
  ""),
 (19, "18h00", "Réel", "Le savoir-faire", "",
  P+"cuisine/coulisses-service.mp4 — mise en place, bons de commande, dressage à la minute, envoi en salle (20-30 s)",
  "19h, la cuisine se met en marche. 🔥\nMise en place, premières commandes, assiettes dressées à la minute : voici ce qui se passe derrière la porte un samedi de décembre chez Da Laura.\nUne équipe, un rythme, et toujours le même soin dans chaque assiette. 🤌\nAbonne-toi pour ne rien rater de nos coulisses.",
  "#DaLaura #FaitMaison #CuisineItalienne #ItalianFood #RestaurantItalienCannes #CannesFood",
  "Abonne-toi pour suivre nos coulisses",
  "Accord de l'équipe filmée"),
 (20, "11h30", "Post", "La communauté", "Résultat du jeu-concours",
  P+"plats/jeu-concours-gagnant.jpg — même visuel que le 17/12 avec « Félicitations ! »",
  "Le tirage au sort a parlé ! 🎉\nFélicitations à @[gagnant ou gagnante], qui remporte un dîner pour deux chez Da Laura : écris-nous en message privé pour organiser ta soirée.\nMerci à vous tous pour vos participations et vos jolis messages. D'autres surprises arrivent bientôt ❤️",
  "#DaLaura #DaLauraCannes #RestaurantCannes #FoodLover #Cannes",
  "Abonne-toi pour ne pas manquer les prochaines surprises",
  "Nom du compte gagnant après tirage"),
 (21, "18h30", "Carrousel", "Cannes et la dolce vita", "Tradition de la Vigilia",
  P+"plats/vigilia-01.jpg à -04.jpg — plats de poissons et fruits de mer",
  "Le 24 décembre au soir, dans le sud de l'Italie, on ne sert pas de viande : c'est la Vigilia, le grand repas de poissons et de fruits de mer. 🐟\nCertaines familles préparent jusqu'à sept plats différents, d'où son surnom : la « fête des sept poissons ».\nGlisse pour découvrir cette tradition, et dis-nous en commentaire : chez toi, le repas de Noël, c'est plutôt poisson ou viande ? 🎄",
  "#DaLaura #CuisineItalienne #ItalianFood #DolceVita #CannesFood #Cannes",
  "Dis-nous en commentaire : poisson ou viande ?",
  "Si le menu du 24 comporte des plats de poisson, le mentionner"),
 (22, "11h30", "Post", "La carte", "Noël (J-2)",
  P+"plats/menu-fetes-2.jpg — plat du menu de Noël, ambiance bougies",
  "Noël, c'est dans deux jours. 🎄\nSi tu cherches encore où réunir ceux que tu aimes, la table de Laura est prête à t'accueillir : un menu de fête à l'italienne, une salle chaleureuse et une équipe aux petits soins.\nLes dernières tables partent vite : réserve via le lien en bio. ✨",
  "#DaLaura #RestaurantItalienCannes #RestaurantCannes #ItalianRestaurant #Cannes #CôteDAzur",
  "Réserve via le lien en bio",
  "Ne publier que s'il reste des places pour Noël"),
 (23, "18h30", "Réel", "Cannes et la dolce vita", "Noël",
  P+"plats/panettone-pandoro.mp4 — panettone et pandoro côte à côte, tranchés, sucre glace (10-15 s)",
  "Panettone ou pandoro ? En Italie, la question divise les familles chaque Noël. 🎄\nD'un côté, la brioche aux fruits confits et aux raisins secs. De l'autre, l'étoile dorée toute moelleuse, saupoudrée de sucre glace.\nEt toi, plutôt panettone ou plutôt pandoro ? Vote en commentaire 👇",
  "#DaLaura #CuisineItalienne #ItalianFood #FoodLover #CannesFood #CôteDAzur",
  "Vote en commentaire",
  ""),
 (24, "11h00", "Post", "L'équipe et Laura", "Réveillon de Noël",
  P+"equipe/equipe-noel.jpg — l'équipe réunie devant le sapin du restaurant",
  "Ce soir, c'est la Vigilia. ✨\nToute l'équipe de Da Laura te souhaite une belle veillée de Noël, entourée de ceux que tu aimes, autour d'une table généreuse.\nPartage ce message avec ceux que tu retrouves ce soir.\nBuona Vigilia 🎄",
  "#DaLaura #DaLauraCannes #CuisineItalienne #DolceVita #Cannes",
  "Partage ce message avec tes proches",
  "Si le restaurant est ouvert le 24 au soir, ajouter « On t'attend ce soir »"),
 (25, "10h00", "Post", "La communauté", "Noël",
  P+"ambiance/table-noel.jpg — table de fête dressée, lumière dorée",
  "Buon Natale ! 🎄\nQue cette journée soit douce, gourmande et pleine de beaux moments partagés.\nMerci de faire partie de la famille Da Laura cette année. ❤️\nDis-nous en commentaire ce qu'il y a sur ta table aujourd'hui.",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #DolceVita #FrenchRiviera",
  "Dis-nous en commentaire ce qu'il y a sur ta table",
  ""),
 (26, "18h00", "Réel", "La communauté", "Bilan de l'année 2026",
  P+"ambiance/retrospective-2026.mp4 — montage des meilleurs moments de l'année (20-30 s)",
  "2026 chez Da Laura, en quelques secondes. ✨\nDes assiettes, des sourires, des soirées d'été et des tablées d'hiver : merci d'avoir fait de cette année une si belle année.\nQuel a été ton moment préféré chez nous ? Raconte-le en commentaire ❤️",
  "#DaLaura #DaLauraCannes #RestaurantCannes #ItalianRestaurant #FoodLover #Cannes #CannesFrance",
  "Raconte ton moment préféré en commentaire",
  "Rushes photo et vidéo de l'année disponibles"),
 (27, "11h30", "Post", "L'équipe et Laura", "Bilan de l'année 2026",
  P+"equipe/equipe-cuisine-salle.jpg — l'équipe de cuisine et de salle réunie",
  "Ils sont là à chaque service, souvent dans l'ombre. ❤️\nEn cuisine comme en salle, notre équipe a donné le meilleur toute l'année pour que chaque soirée chez Da Laura soit réussie.\nGrazie mille à eux, et à toi qui viens partager leur travail à table.\nLaisse-leur un petit mot en commentaire, on leur transmettra. ✨",
  "#DaLaura #RestaurantItalienCannes #CuisineItalienne #FaitMaison #CannesRestaurant",
  "Laisse un mot à l'équipe en commentaire",
  "Accord de l'équipe pour la photo"),
 (28, "18h30", "Post", "La carte", "Saint-Sylvestre (J-3)",
  P+"plats/menu-reveillon.jpg — plat du menu du 31, table élégante",
  "Plus que trois jours avant le réveillon. ✨\nPour passer à 2027 en beauté, la cuisine prépare un menu de Saint-Sylvestre à l'italienne, dans une ambiance élégante et festive.\nIl reste encore quelques tables : réserve la tienne via le lien en bio. 🎉",
  "#DaLaura #DaLauraCannes #RestaurantCannes #DolceVita #Cannes #FrenchRiviera",
  "Réserve ta table du 31 via le lien en bio",
  "Ne publier que s'il reste des places pour le 31"),
 (29, "11h30", "Carrousel", "Cannes et la dolce vita", "Traditions du Nouvel An italien",
  P+"plats/capodanno-01.jpg à -04.jpg — lentilles, cotechino, touche de rouge dans la déco",
  "Comment fête-t-on le Nouvel An en Italie ? 🇮🇹\nDes lentilles pour la prospérité, du cotechino pour l'abondance et… une touche de rouge sur soi pour porter chance toute l'année.\nGlisse pour découvrir ces traditions, et dis-nous laquelle tu vas adopter ce 31 décembre. ✨",
  "#DaLaura #CuisineItalienne #ItalianFood #DolceVita #CannesFood #CôteDAzur",
  "Dis-nous en commentaire quelle tradition tu adoptes",
  ""),
 (30, "18h30", "Réel", "Le savoir-faire", "Saint-Sylvestre (J-1)",
  P+"cuisine/preparatifs-reveillon.mp4 — mise en place, nappes, cuisine en effervescence (sans bouteilles au premier plan)",
  "J-1 avant le réveillon : la maison se prépare. ✨\nMise en place, nappes repassées, cuisine en pleine effervescence et dernières touches de décoration : on veut que ta soirée soit parfaite.\nPas encore de table ? Écris-nous en message privé.\nCi vediamo domani 🎉",
  "#DaLaura #DaLauraCannes #RestaurantItalienCannes #ItalianRestaurant #Cannes #CannesFrance",
  "Écris-nous en message privé pour une dernière table",
  "Ne pas mettre de bouteilles ou de coupes au premier plan (loi Évin)"),
 (31, "17h00", "Post", "La communauté", "Saint-Sylvestre",
  P+"ambiance/nouvel-an.jpg — salle prête pour le réveillon, bougies, touches dorées",
  "Dernier soir de l'année. ✨\nMerci pour chaque table réservée, chaque message, chaque assiette partagée en 2026. On te souhaite une année 2027 pleine de bonheur, de gourmandise et de beaux moments.\nÀ minuit, les yeux vers la baie de Cannes pour le feu d'artifice… Buon anno 🎉\nOn se retrouve très vite chez Da Laura.",
  "#DaLaura #DaLauraCannes #RestaurantCannes #DolceVita #Cannes #FrenchRiviera",
  "On se retrouve très vite chez Da Laura",
  ""),
]

# (jour, heures, photo, theme, legende, cta, a_valider)
STORIES = [
 (1, "11h30 · 15h · 18h30", "Vidéos courtes de la salle décorée (à filmer)", "L'ambiance",
  "1. Vidéo de la salle décorée, texte « Décembre chez Da Laura ✨ »\n2. Sondage « Prêt pour les fêtes ? » Oui 🎄 / Toujours !\n3. Partage du carrousel du jour\n4. Sticker lien « Réserver »", "Sticker lien « Réserver »", ""),
 (2, "10h · 15h · 18h30", "Coulisses des pâtes fraîches le matin (à filmer)", "Le savoir-faire",
  "1. Vidéo des pâtes tirées le matin, texte « 9h, les pâtes du jour 🍝 »\n2. Quiz « Combien d'œufs pour 1 kg de farine ? » 5 / 10 ✅ / 15\n3. Partage du réel du jour", "Sticker quiz + partage du réel", ""),
 (3, "11h30 · 15h · 19h", "Visuel du menu de fêtes", "La carte",
  "1. Visuel « Nos menus de fêtes sont là 🎄 »\n2. Boîte à questions « Une question sur nos menus de Noël ? »\n3. Sticker lien « Réserver ma soirée »", "Sticker lien « Réserver ma soirée »", "Menus de fêtes validés"),
 (4, "11h30 · 15h · 18h30", "Photo du plat du jour", "La carte",
  "1. Photo « Suggestion du jour » (nom du plat en surimpression)\n2. Sondage « Ce soir, tu choisis… » Risotto / Ragù\n3. Sticker lien « Réserver pour le week-end »", "Sticker lien « Réserver »", "Plat du jour"),
 (5, "12h · 17h · 19h30", "Mise en place du samedi (à filmer)", "L'ambiance",
  "1. Vidéo de la mise en place, texte « Samedi soir, on se prépare ✨ »\n2. Partage du réel du jour\n3. Sticker lien « Réserver ce soir »", "Sticker lien « Réserver »", ""),
 (6, "11h30 · 16h · 19h", "Portrait de Laura", "L'équipe et Laura",
  "1. Photo de Laura, texte « Pose ta question à Laura ❤️ »\n2. Boîte à questions\n3. Partage du post du jour", "Boîte à questions", ""),
 (7, "11h30 · 15h · 18h30", "Photo d'une grande tablée", "La carte",
  "1. Photo d'une grande tablée, texte « Ton repas de fin d'année chez nous ? »\n2. Sondage « Repas d'équipe prévu ? » Oui / Pas encore\n3. Texte « Écris-nous en message privé ✨ »", "Écris-nous en message privé", "Offre groupes"),
 (8, "11h30 · 15h · 18h30", "Installation du sapin en accéléré (à filmer)", "Cannes et la dolce vita",
  "1. Vidéo du sapin installé en accéléré 🎄\n2. Quiz « En Italie, on décore le sapin le… » 1er décembre / 8 décembre ✅ / 24 décembre\n3. Partage du carrousel du jour", "Sticker quiz", ""),
 (9, "11h30 · 15h · 18h30", "Coulisses du montage du tiramisu (à filmer)", "Le savoir-faire",
  "1. Vidéo du montage, texte « Le dessert de demain se prépare aujourd'hui ☕ »\n2. Sondage « Ton dessert italien préféré ? » Tiramisu / Panna cotta\n3. Partage du réel du jour", "Partage du réel", ""),
 (10, "11h30 · 15h · 19h", "Photo de la carte cadeau", "La carte",
  "1. Photo de la carte cadeau, texte « Idée cadeau 🎁 »\n2. Texte « Un dîner à offrir, ça se commande en message privé »\n3. Partage du post du jour", "Écris-nous en message privé", "Carte cadeau confirmée"),
 (11, "11h30 · 15h · 18h30", "Photo du plat du week-end", "La carte",
  "1. Photo « La suggestion du chef ce week-end »\n2. Partage du post du jour, avec la mention loi Évin visible\n3. Sticker lien « Réserver »", "Sticker lien « Réserver »", "Garder la mention loi Évin sur le partage"),
 (12, "12h · 17h · 19h30", "Burrata en gros plan", "La carte",
  "1. Photo de la burrata, texte « Elle t'attend ce soir 🤍 »\n2. Sondage « La burrata, tu la préfères… » Nature / Avec tomates\n3. Partage du réel du jour", "Sondage + partage du réel", ""),
 (13, "11h · 15h · 18h", "Table familiale du dimanche midi", "La communauté",
  "1. Photo de la table, texte « Bon dimanche ❤️ »\n2. Réponses de Laura aux questions du 6 décembre\n3. Sticker lien « Réserver »", "Sticker lien « Réserver »", "Réponses de Laura"),
 (14, "11h30 · 15h · 18h30", "Gros plans des produits italiens", "Le savoir-faire",
  "1. Gros plan sur le parmesan, texte « Direction l'Italie 🇮🇹 »\n2. Quiz « Le Parmigiano Reggiano vient de… » Émilie-Romagne ✅ / Sicile / Toscane\n3. Partage du carrousel du jour", "Sticker quiz", ""),
 (15, "11h30 · 15h · 18h30", "Stories de clients qui nous ont identifiés", "La communauté",
  "1. Partage de 2 ou 3 stories de clients\n2. Texte « Merci pour vos jolis messages ✨ »\n3. Texte « Identifie-nous, on republie ! »", "Identifie-nous dans tes stories", "Accord des clients republiés"),
 (16, "11h30 · 15h · 18h30", "Coulisses du dressage de la table de fête", "L'ambiance",
  "1. Vidéo du dressage, texte « La table des fêtes se prépare 🕯️ »\n2. Sondage « Nappe blanche ou nappe rouge ? »\n3. Partage du réel du jour", "Partage du réel", ""),
 (17, "11h30 · 15h · 19h", "Visuel du jeu-concours", "La communauté",
  "1. Visuel « Jeu-concours : un dîner pour deux à gagner 🎁 »\n2. Texte « Participe sur notre dernier post »\n3. Sticker compte à rebours « Fin du jeu », 19/12 à 23h59", "Participe sur le post", "Règlement"),
 (18, "12h · 17h · 19h", "Croisette illuminée (à filmer)", "Cannes et la dolce vita",
  "1. Vidéo des illuminations, texte « Cannes en décembre ✨ »\n2. Partage du post du jour\n3. Sticker lien « Réserver »", "Sticker lien « Réserver »", ""),
 (19, "12h · 17h · 19h30", "Coulisses du service", "La communauté",
  "1. Texte « Dernier jour pour participer au jeu-concours 🎁 »\n2. Vidéo de la cuisine en plein service\n3. Partage du réel du jour", "Participe sur le post", ""),
 (20, "11h30 · 15h · 18h30", "Vidéo du tirage au sort", "La communauté",
  "1. Vidéo du tirage au sort 🎉\n2. Annonce du compte gagnant\n3. Texte « Merci à tous ❤️ »", "Abonne-toi pour les prochaines surprises", ""),
 (21, "11h30 · 15h · 18h30", "Photo d'un plat de poisson", "Cannes et la dolce vita",
  "1. Quiz « À la Vigilia, combien de poissons sont servis selon la tradition ? » 3 / 7 ✅ / 12\n2. Sondage « Noël : poisson ou viande ? »\n3. Partage du carrousel du jour", "Sticker quiz", ""),
 (22, "11h · 15h · 18h30", "Préparation du menu de Noël", "La carte",
  "1. Sticker compte à rebours « Noël »\n2. Coulisses de la préparation du menu\n3. Sticker lien « Réserver ma table »", "Sticker lien « Réserver »", "Places restantes pour Noël"),
 (23, "11h30 · 15h · 16h · 18h30", "Panettone et pandoro", "Cannes et la dolce vita",
  "1. Sondage « Panettone ou pandoro ? » 🎄\n2. Résultat du sondage en fin de journée\n3. Photo des illuminations, texte « Parade de Noël à 17h30 : après, viens te réchauffer chez nous »\n4. Partage du réel du jour", "Sondage + sticker lien « Réserver »", "Horaire de la parade (17h30, départ rue Meynadier) à reconfirmer"),
 (24, "11h · 16h · 19h", "Vidéo de l'équipe", "L'équipe et Laura",
  "1. Vidéo de l'équipe qui souhaite une belle veillée ✨\n2. Coulisses du service du soir (si le restaurant est ouvert)\n3. Partage du post du jour", "Partage du post", "Ouverture le 24"),
 (25, "10h · 13h · 18h", "Table de Noël", "La communauté",
  "1. Photo de la table, texte « Buon Natale ! 🎄 »\n2. Partage du post du jour\n3. Boîte à questions « Qu'y a-t-il sur ta table aujourd'hui ? »", "Boîte à questions", ""),
 (26, "11h30 · 15h · 18h30", "Moments forts de l'année", "La communauté",
  "1. Texte « En Italie, le 26, on fête Santo Stefano : la fête continue en famille ❤️ »\n2. Boîte à questions « Ton plus beau souvenir chez Da Laura en 2026 ? »\n3. Partage du réel du jour", "Boîte à questions", ""),
 (27, "11h30 · 15h · 18h30", "Photos de l'équipe", "L'équipe et Laura",
  "1. Partage des réponses du 26 décembre\n2. Photo de l'équipe, texte « Merci à eux ✨ »\n3. Partage du post du jour", "Laisse un mot à l'équipe", ""),
 (28, "11h30 · 15h · 18h30", "Visuel du menu du 31", "La carte",
  "1. Sticker compte à rebours « Réveillon »\n2. Visuel du menu de la Saint-Sylvestre\n3. Sticker lien « Réserver ma table »", "Sticker lien « Réserver »", "Places restantes pour le 31"),
 (29, "11h30 · 15h · 18h30", "Lentilles et cotechino", "Cannes et la dolce vita",
  "1. Quiz « En Italie, pour porter chance le 31, on porte du… » Rouge ✅ / Vert / Blanc\n2. Partage du carrousel du jour\n3. Sondage « Tu adoptes les lentilles du Nouvel An ? » Oui / Pourquoi pas", "Sticker quiz", ""),
 (30, "11h30 · 15h · 18h30", "Coulisses des préparatifs", "Le savoir-faire",
  "1. Vidéo des préparatifs, texte « J-1 ✨ »\n2. Partage du réel du jour\n3. Texte « Une dernière table ? Écris-nous en message privé »", "Écris-nous en message privé", ""),
 (31, "11h30 · 17h · 23h50", "Salle prête pour le réveillon + vidéo de l'équipe", "La communauté",
  "1. Vidéo de la salle prête, texte « Ce soir, on fête 2027 🎉 »\n2. Sticker compte à rebours « Minuit »\n3. Vidéo de l'équipe : « Buon anno ! » (juste avant minuit)", "Partage du post", ""),
]

TEXTES = {1:"Noël chez Da Laura",2:"Pâtes fraîches, faites main",3:"Nos menus de fêtes",4:"La carte d'hiver",5:"Samedi soir",6:"Laura, l'âme de la maison",7:"Tes repas de fin d'année",8:"L'Immacolata",9:"Le vrai tiramisu",10:"Offre un dîner",11:"L'accord parfait",12:"Burrata",13:"Le dimanche en famille",14:"Les produits d'Italie",15:"Merci pour vos mots",16:"La table des fêtes",17:"Un dîner pour deux à gagner",18:"Cannes en décembre",19:"Dans nos cuisines",20:"Félicitations !",21:"La Vigilia",22:"Noël, c'est dans deux jours",23:"Panettone ou pandoro ?",24:"Buona Vigilia",25:"Buon Natale",26:"2026 en images",27:"Grazie mille",28:"Réveillon : J-3",29:"Le Nouvel An à l'italienne",30:"Réveillon : J-1",31:"Buon anno 2027"}

TEMPS_FORTS = [
    ("1er déc.", "Ouverture du mois des fêtes", "Carrousel de la salle décorée"),
    ("3 déc.", "Menus de Noël et du 31", "Annonce tôt pour lancer les réservations"),
    ("7 déc.", "Repas de fin d'année", "Offre groupes et entreprises"),
    ("8 déc.", "Immacolata", "Tradition italienne du sapin, décoration du restaurant"),
    ("10 déc.", "Cadeaux de Noël", "Carte cadeau (à confirmer)"),
    ("17 → 20 déc.", "Jeu-concours de Noël", "Dîner pour deux à gagner, pour l'engagement et les abonnés"),
    ("18 déc.", "Illuminations et village de Noël du Palm Beach (3 déc. → 3 janv.)", "Pilier « Cannes et la dolce vita »"),
    ("21 → 25 déc.", "Vigilia et Noël", "Tradition des sept poissons, panettone ou pandoro, vœux"),
    ("23 déc.", "Parade lumineuse de Noël (17h30, rue Meynadier)", "Story « après la parade, viens te réchauffer »"),
    ("26 → 27 déc.", "Santo Stefano et bilan 2026", "Rétrospective et remerciements à l'équipe"),
    ("28 → 31 déc.", "Saint-Sylvestre et feu d'artifice sur la baie à minuit", "Dernières tables, traditions du Capodanno, vœux"),
]
NON_RETENUS = "Non retenus : le Black Friday, déjà passé ; les soldes d'hiver, qui ne commencent que le 6 janvier 2027 ; le Téléthon (4-5 déc.), éventuellement en simple story de soutien. Détail dans la veille."
A_VALIDER = [
    "**Ouverture et horaires** les 24, 25 et 31 décembre, et le dimanche midi.",
    "**Menus de fêtes** : contenu et prix, à insérer dans la légende du 3 décembre.",
    "**Carte cadeau** : existe-t-elle ? Quels montants ? Achat en ligne ou sur place ?",
    "**Offre groupes** : capacité d'accueil, privatisation.",
    "**Jeu-concours** : dotation (sans alcool), règlement accessible en bio, nom exact du compte Instagram.",
    "**Histoire de Laura** (post du 6 décembre) : à ajouter aussi dans la fiche marque.",
    "**Plats, vins et produits** cités : à vérifier par rapport à la carte réelle.",
    "**Tournages (d'après la veille)** : dans chaque réel, au moins un plan avec une personne visible (Laura, le chef, une main en action) et le plan le plus gourmand dans les 3 premières secondes. Images naturelles, peu filtrées.",
    "**Droit à l'image** : accord des clients et de l'équipe filmés ou photographiés.",
    "**Loi Évin** : mention obligatoire sur le post du 11 décembre et sur son partage en story. Pas de bouteilles ni de coupes au premier plan dans les autres visuels.",
]


# ---- Contrat Essentielle : 8 publications et 2 réels par mois, stories = plats du jour ----
# ---- Contrat Essentielle : 8 publications, 2 réels, 20 stories (le bloc du 27/11 en fin de fichier fait foi) ----
R = "photos/da-laura/compte-instagram/recadrees/"
H_IG = "#DaLaura #DaLauraCannes #RestaurantItalienCannes #DolceVita #Cannes #FrenchRiviera"
import json as _json
def _reel(j, nom, pilier, tf, av=""):
    d = _json.load(open(f"outils/reels/{nom}.json", encoding="utf-8"))
    return (j, "18h30", "Réel", pilier, tf,
            f"reels/da-laura/{nom}.mp4 — montage prêt (version TikTok : reels/da-laura/{nom}-tiktok.mp4)",
            d["legende"], d["hashtags"], "Réserve ta table via le lien en bio", av)
REMPLACER = {
 1: (1, "18h30", "Carrousel", "L'ambiance", "Lancement du compte",
     R+"facade-fiat-500-rouge.jpg + "+R+"facade-terrasse.jpg + photos/da-laura/ambiance/salle-guirlandes.jpg + "+R+"table-assiette-da-laura.jpg + photos/da-laura/ambiance/ardoise-piatti-del-giorno.jpg — la façade, la terrasse, la salle, la table et Laura",
     "Bienvenue chez Da Laura. ✨\nDepuis 1992, on cuisine à l'italienne à Cannes : pâtes faites maison, ingrédients venus d'Italie et une terrasse où l'on aime prendre son temps.\nGlisse pour entrer dans la maison, et réserve ta table via le lien en bio. 🍝",
     H_IG, "Réserve ta table via le lien en bio", ""),
 2: _reel(2, "2026-12-02-decouverte-da-laura", "L'ambiance", "Lancement du compte", "Desserts « maison » à confirmer avec Laura"),
 8: (8, "11h30", "Carrousel", "Le savoir-faire", "",
     R+"ravioli-faconnes-main.jpg + photos/da-laura/cuisine/gnocchi-faits-main.jpg + photos/da-laura/cuisine/pates-fraiches-rigatoni.jpg + "+R+"pates-poele-flamme.jpg + photos/da-laura/plats/ravioli-truffe.jpg — les pâtes, de la main du chef à l'assiette",
     "Ici, les pâtes sont faites maison. 🍝\nRavioli façonnés à la main, gnocchi, rigatoni tout juste sortis de la machine : chaque forme a sa recette et sa sauce.\nGlisse pour les découvrir, et dis-nous en commentaire laquelle tu préfères. 👇",
     "#DaLaura #PastaFresca #PâtesFraîches #FaitMaison #CuisineItalienne #CannesFood", "Dis-nous en commentaire ta forme préférée", ""),
 9: _reel(9, "2026-12-09-geste-du-chef", "Le savoir-faire", ""),
 16: _reel(16, "2026-12-16-pause-douceur", "La carte", "", "Noms exacts des desserts à confirmer avec Laura"),
 23: _reel(23, "2026-12-23-fetes-da-laura", "L'ambiance", "Fêtes de fin d'année", "Ouverture les 24, 25 et 26 décembre"),
 30: _reel(30, "2026-12-30-merci-2026", "La communauté", "Fin d'année", ""),
}
TEXTES.update({1: "Bienvenue chez Da Laura", 2: "La cucina autentica", 8: "Nos pâtes faites maison", 9: "Le geste du chef",
               16: "La pause douceur", 23: "Pour les fêtes", 30: "Merci pour 2026"})
FEED = [REMPLACER.get(r[0], r) for r in FEED]
GARDER = {1, 2, 3, 6, 8, 9, 14, 16, 21, 23, 25, 29, 30}
FEED = [r for r in FEED if r[0] in GARDER]
PHOTOS_REELLES = {
 6: "photos/da-laura/ambiance/ardoise-piatti-del-giorno.jpg — Laura et son ardoise sur la terrasse",
 14: "photos/da-laura/plats/planche-fromages-charcuterie.jpg + photos/da-laura/plats/ravioli-truffe.jpg + photos/da-laura/plats/pappardelle-prosciutto-huile.jpg — fromages et charcuterie, truffe, huile d'olive",
 21: "photos/da-laura/plats/spaghetti-crevettes.jpg + "+R+"risotto-crevettes.jpg + "+R+"spaghetti-crevettes-sauce.jpg — les plats de la mer de Da Laura",
 25: R+"lustre-bougies.jpg — le lustre aux bougies de la salle, ambiance de fête",
}
FEED = [r[:5] + (PHOTOS_REELLES.get(r[0], r[5]),) + r[6:] for r in FEED]
STORIES = []
TEMPS_FORTS = [
    ("Semaine 1 (1-6 déc.)", "Lancement du compte", "Carrousel « Bienvenue chez Da Laura » + réel « La cucina autentica »"),
    ("Semaine 2 (7-13 déc.)", "Le savoir-faire", "Carrousel « Nos pâtes faites maison » + réel « Le geste du chef »"),
    ("Semaine 3 (14-20 déc.)", "Produits et douceurs", "Carrousel « Les produits d'Italie » + réel « La pause douceur »"),
    ("Semaine 4 (21-27 déc.)", "Vigilia et Noël", "Carrousel « La Vigilia » + réel « Pour les fêtes » + post « Buon Natale »"),
    ("Semaine 5 (28-31 déc.)", "Saint-Sylvestre", "Carrousel « Le Nouvel An à l'italienne » + réel « Merci pour 2026 »"),
]
NON_RETENUS = ""  # remplacé plus bas (contrat Essentielle)
A_VALIDER = [
    "**Ouverture et horaires** les 24, 25 et 31 décembre ; **menus de fêtes** et prix pour le post du 3 décembre.",
    "**Histoire de Laura** (post du 6 décembre) ; **desserts** : noms exacts et « faits maison » à confirmer.",
    "**Photos en attente** : lentilles et cotechino (carrousel du 29), sinon remplacement par des photos existantes. Le post du 25 utilise le lustre aux bougies de la salle.",
    "**Qualité** : plusieurs photos viennent de la grille du compte (374 px de large) : demander les originaux pour une netteté parfaite.",
    "**Loi Évin** : les photos avec spritz ou coupe de champagne sont écartées.",
]

# ---- 27/11/2026 : tout le mois refait avec les photos du shooting professionnel de Cannes ----
C = "photos/da-laura/cannes/"
def _c(*noms): return " + ".join(C + n + ".jpg" for n in noms)
NOUVELLES = {
 1: (_c("facade-terrasse", "enseigne-triangle", "salle-banquette-jaune", "terrasse-fauteuils", "epicerie", "facade-rue") + " — la terrasse, l'enseigne, la salle, l'épicerie : entrer chez Da Laura",
     "Bienvenue chez Da Laura. ✨\nUne terrasse au cœur de Cannes, une salle où l'on prend son temps et la cucina autentica, dal 1992.\nGlisse pour entrer dans la maison, et réserve ta table via le lien en bio. 🍝"),
 3: (_c("table-dressee-chaises-jaunes") + " — une table dressée, prête pour les fêtes", None),
 6: ("photos/da-laura/laura/laura-portrait.jpg — Laura dans sa salle", None),
 8: (_c("tagliatelle-machine", "pappardelle-fraiches", "gnocchi-roules", "rigatoni-mains-chef", "poele-flamme-pates", "spaghetti-champignons") + " — des pâtes fraîches tirées le matin jusqu'à l'assiette",
     "Ici, les pâtes sont faites maison. 🍝\nTagliatelle tout juste sorties de la machine, gnocchi roulés à la main, rigatoni du jour… puis un passage à la poêle avant d'arriver dans ton assiette.\nGlisse pour suivre le chemin, et dis-nous en commentaire ta forme préférée. 👇"),
 14: (_c("trancheuse-prosciutto", "burrata-prosciutto-gros-plan", "planche-antipasti", "burrata-tomates", "chef-citrons", "burrata-truffe") + " — prosciutto tranché, burrata, antipasti, citrons, truffe",
     "Les produits d'Italie, à la table de Da Laura. 🇮🇹\nProsciutto tranché minute, burrata crémeuse, antipasti à partager, citrons ensoleillés et truffe râpée : de beaux produits, travaillés simplement.\nGlisse pour les découvrir, et enregistre ce post pour ta prochaine envie d'Italie. 🌿"),
 21: (_c("palourdes", "langoustines-pates", "chef-spaghetti-crevettes", "huile-spaghetti-crevettes", "poelee-mer") + " — les plats de la mer de Da Laura",
     None),
 25: (_c("terrasse-fauteuils") + " — le salon chaleureux de Da Laura, ambiance de fête", None),
 29: (_c("fusilli-piment", "tiramisu-fraise", "risotto-safran-jambon", "table-bougie", "poele-flambee") + " — une touche de rouge porte-bonheur et des plats de fête",
     "Comment fête-t-on le Nouvel An en Italie ? 🇮🇹\nOn porte une touche de rouge pour la chance, on partage un grand repas et on finit sur une note sucrée.\nGlisse pour notre version Da Laura, et dis-nous en commentaire ta tradition du 31. ✨"),
}
# Fermetures (info du 27/11/2026) : le 24 décembre au soir et le 25 décembre toute la journée.
NOUVELLES[3] = (NOUVELLES[3][0], "Les fêtes approchent, et ta table chez Da Laura aussi. 🎄\nPour la Saint-Sylvestre, la cuisine prépare un menu de fête à l'italienne : [détail du menu et prix à compléter].\nÀ noter : le 24 décembre, on t'accueille au déjeuner ; le 24 au soir et le jour de Noël, toute l'équipe est en famille.\nLes places sont limitées : réserve dès maintenant via le lien en bio. ✨")
NOUVELLES[25] = (NOUVELLES[25][0], "Buon Natale ! 🎄\nAujourd'hui, toute l'équipe de Da Laura est en famille, et on te souhaite d'en profiter autant que nous.\nQue cette journée soit douce, gourmande et pleine de beaux moments partagés. ❤️\nDis-nous en commentaire ce qu'il y a sur ta table aujourd'hui.")
FEED = [r[:5] + ((NOUVELLES[r[0]][0], NOUVELLES[r[0]][1] or r[6]) if r[0] in NOUVELLES else (r[5], r[6])) + r[7:] for r in FEED]
FEED = [REMPLACER[r[0]] if r[0] in (2, 9, 16, 23, 30) else r for r in FEED]  # réels : légendes relues dans les nouveaux plans
TEXTES.update({14: "Les produits d'Italie", 21: "La Vigilia", 29: "Capodanno", 25: "Buon Natale"})
A_VALIDER = [
    "**Photos** : toutes viennent du shooting professionnel de Cannes (charte naturelle appliquée). Les photos de Mougins sont gardées à part (autre lieu).",
    "**Post du 6 décembre** : photo de Laura (shooting) et son histoire à compléter avec elle.",
    "**Fêtes** : fermé le 24 au soir et le 25 toute la journée (confirmé). Reste à confirmer : ouverture du 31 et menu de la Saint-Sylvestre (post du 3).",
    "**Loi Évin** : aucune photo avec verre de vin, spritz ou coupe de champagne.",
]

# ---- 27/11/2026 : CONTRAT ESSENTIELLE = 2 RÉELS (jamais 5). Réels réalisés par l'utilisatrice : créneaux des 9 et 23 décembre. ----
FEED = [r for r in FEED if not (r[2] == "Réel" and r[0] not in (9, 23))]
FEED = [r[:5] + ("Réel réalisé par la community manager (Instagram + TikTok) : idée et légende proposées ci-dessous",) + r[6:] if r[2] == "Réel" else r for r in FEED]
TEMPS_FORTS = [
    ("Semaine 1 (1-6 déc.)", "Lancement du compte", "Carrousel « Bienvenue chez Da Laura » + posts « Nos menus de fêtes » et « Laura, l'âme de la maison »"),
    ("Semaine 2 (7-13 déc.)", "Le savoir-faire", "Carrousel « Nos pâtes faites maison » + réel n° 1 « Le geste du chef » (9 déc.)"),
    ("Semaine 3 (14-20 déc.)", "Les produits", "Carrousel « Les produits d'Italie »"),
    ("Semaine 4 (21-27 déc.)", "Vigilia et Noël", "Carrousel « La Vigilia » + réel n° 2 « Pour les fêtes » (23 déc.) + post « Buon Natale »"),
    ("Semaine 5 (28-31 déc.)", "Nouvel An", "Carrousel « Capodanno »"),
]
NON_RETENUS = "Formule Essentielle : 8 publications (5 carrousels, 3 posts), 2 réels (Instagram + TikTok, réalisés par la community manager), 20 stories « Piatti del giorno » (du mardi au samedi à 11h, sauf le 25 décembre, fermé, remplacé par le 29)."
A_VALIDER = [
    "**Contrat Essentielle** : 8 publications, 2 réels, 20 stories. Rien de plus n'est prévu.",
    "**Photos** : toutes viennent du shooting professionnel de Cannes (charte naturelle appliquée).",
    "**Post du 6 décembre** : photo de Laura (shooting) et son histoire à compléter avec elle.",
    "**Fêtes** : fermé le 24 au soir et le 25 toute la journée. À confirmer : ouverture du 26 et du 31, menu de la Saint-Sylvestre (post du 3).",
    "**Loi Évin** : aucune photo avec verre de vin, spritz ou coupe de champagne.",
]

# ---- 27/11/2026 : carrousel du 1er décembre choisi dans le Drive « Photo Cannes » (_DSC8100, 7635, 8110, 8069, 7629, 0662) ----
FEED = [r[:5] + (_c("facade-rue", "enseigne-triangle", "terrasse-rue", "salle-banquette-jaune", "epicerie", "table-assiettes-peintes")
         + " — on arrive au coin de la rue, l'enseigne, la terrasse, la salle, l'épicerie, puis une table dressée qui t'attend",
         "Entre, tu es chez nous. ✨\nUne terrasse au coin de la rue, une salle pleine de couleurs, une épicerie remplie de produits italiens… Chez Da Laura, la cucina autentica se vit depuis 1992.\nGlisse pour faire le tour de la maison, puis choisis ta table : elle est déjà dressée. 🇮🇹\n📍 8 rue du 24 Août, Cannes · Réservations : 04 93 38 40 51",
         ) + r[7:] if r[0] == 1 else r for r in FEED]
# Fêtes : ouvert le 26 et le 31 au soir (carte réduite le 31)
FEED = [r[:6] + (r[6].replace("Pour la Saint-Sylvestre, la cuisine prépare un menu de fête à l'italienne : [détail du menu et prix à compléter].", "Le 31 au soir, on fête la Saint-Sylvestre avec une carte réduite, pensée pour l'occasion.").replace("Les places sont limitées : réserve", "Les places sont limitées ce soir-là : réserve"),) + r[7:] if r[0] == 3 else r for r in FEED]
A_VALIDER = [a for a in A_VALIDER if not a.startswith("**Fêtes**")] + ["**Fêtes** : fermé le 24 au soir et le 25 toute la journée ; ouvert le 26 et le 31 au soir (carte réduite)."]

# ---- 27/11/2026 : légendes des carrousels relues et adaptées aux photos choisies ----
_LEG = {
 8: ("Ici, les pâtes naissent le matin. 🍝\nLes tagliatelle sortent de la machine, les pappardelle sèchent sur le plan de travail, les gnocchi sont roulés un à un… puis tout passe à la poêle, sur le feu, juste avant d'arriver dans ton assiette.\nGlisse pour suivre le chemin, et dis-nous en commentaire : tu es plutôt tagliatelle, gnocchi ou rigatoni ? 👇\n📍 8 rue du 24 Août, Cannes · Réservations : 04 93 38 40 51", "#DaLaura #DaLauraCannes #PastaFresca #PâtesFraîches #FaitMaison #CuisineItalienne #RestaurantItalienCannes"),
 14: ("L'Italie, produit par produit. 🇮🇹\nLe prosciutto tranché à la minute, la burrata crémeuse, une belle planche d'antipasti à partager, les citrons du Sud et la truffe en fines lamelles : quand les produits sont beaux, on les travaille simplement.\nGlisse pour les découvrir, et enregistre ce post pour ta prochaine envie d'Italie. 🌿\n📍 8 rue du 24 Août, Cannes · Réservations : 04 93 38 40 51", "#DaLaura #DaLauraCannes #CuisineItalienne #ItalianFood #Antipasti #Burrata #RestaurantItalienCannes"),
 21: ("En Italie, le soir du 24 décembre, c'est la Vigilia : un grand repas de poissons et de fruits de mer, sans viande. 🐟\nDans certaines familles du Sud, on prépare jusqu'à sept plats : on l'appelle la « fête des sept poissons ».\nChez Da Laura, la mer s'invite à table : palourdes, langoustines, spaghetti aux crevettes… Glisse pour les découvrir, et dis-nous en commentaire : chez toi, Noël, c'est poisson ou viande ? 🎄\n📍 8 rue du 24 Août, Cannes · Réservations : 04 93 38 40 51", "#DaLaura #DaLauraCannes #CuisineItalienne #ItalianFood #FruitsDeMer #RestaurantItalienCannes #Cannes"),
 29: ("Comment fête-t-on le Nouvel An en Italie ? 🇮🇹\nOn porte une touche de rouge pour la chance, on partage un bon repas et on finit toujours sur une note sucrée.\nGlisse pour notre version Da Laura : du piment rouge, du safran, un dolce aux fraises et une flamme pour fêter 2027. ✨\nLe 31 au soir, on t'accueille avec une carte réduite, pensée pour l'occasion : réserve ta table via le lien en bio.\n📍 8 rue du 24 Août, Cannes · Réservations : 04 93 38 40 51", "#DaLaura #DaLauraCannes #CuisineItalienne #DolceVita #Capodanno #RestaurantItalienCannes #Cannes"),
}
FEED = [r[:6] + (_LEG[r[0]][0], _LEG[r[0]][1]) + r[8:] if r[0] in _LEG else r for r in FEED]

if __name__ == '__main__':
    import sys
    from rendu import rendre
    print(rendre(sys.argv[1], 2026, 12, 'décembre', 'da-laura-2026-12', FEED, STORIES, TEXTES, TEMPS_FORTS, NON_RETENUS, A_VALIDER, P, STORY_TAGS), 'lignes')
