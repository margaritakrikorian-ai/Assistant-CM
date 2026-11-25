const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require("/root/.claude/skills/synced/b9a3ddc6-8a95-409a-b3ac-b8eea1a139e3_90ee0b07-47bf-455b-ac9a-75d6dee4c777/pptx/scripts/apply_theme.js");

// Palette tirée de l'identité Mamo : or du logo, crème, espresso, rouge du bar, olive des assiettes
const HEX = {
  espresso: "1A1512", blanc: "FFFFFF", bordeaux: "7A2E22", creme: "F5EFE4",
  or: "DBB48E", rouge: "A63D2F", olive: "5E7A4A", terre: "C98F6B", sable: "E8D3B0", vertNuit: "2F4A3A",
};
const THEME = {
  name: "Mamo Benvenuti",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: HEX.espresso, lt1: HEX.blanc, dk2: HEX.bordeaux, lt2: HEX.creme,
    accent1: HEX.or, accent2: HEX.rouge, accent3: HEX.olive, accent4: HEX.terre, accent5: HEX.sable, accent6: HEX.vertNuit,
    hlink: HEX.bordeaux, folHlink: HEX.bordeaux,
  },
};

async function icon(Comp, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  pres.title = "Mamo Michelangelo · Proposition réseaux sociaux";
  pres.author = "Margaux Krikorian";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  const FOOT = "Mamo Michelangelo · Proposition d'accompagnement réseaux sociaux · Margaux Krikorian";
  pres.defineSlideMaster({
    title: "CONTENU",
    background: { color: C.background1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.95, fontSize: 32, bold: true, color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
      { text: { text: FOOT, options: { x: 0.6, y: 7.0, w: 9, h: 0.3, fontSize: 10, color: C.text2, margin: 0 } } },
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.text2, align: "right" },
  });
  pres.defineSlideMaster({
    title: "SOMBRE",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.3, w: 5.6, h: 1.6, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.05, w: 5.4, h: 1.7, fontSize: 18, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });

  const SOMBRES = [HEX.rouge, HEX.olive, HEX.bordeaux, HEX.vertNuit, HEX.espresso];
  const logoHaut = (s) => s.addImage({ path: "photos/logo.png", x: 0.8, y: 1.0, w: 2.6, h: 2.6 * 202 / 700, altText: "Logo Mamo Michelangelo", objectName: "logo" });
  const photoDroite = (s, nom) => {
    s.addImage({ path: "photos/" + nom + ".jpg", x: 6.667, y: 0, w: 6.667, h: 7.5, altText: "Photo de Mamo Michelangelo", objectName: "photo-" + nom });
    s.addText("Photo : mamo-michelangelo.com", { x: 0.8, y: 7.0, w: 4.0, h: 0.3, fontSize: 10, color: C.background2, margin: 0, isTextBox: true, objectName: "credit-" + nom });
  };
  const carte = (s, x, y, w, h, color, name) =>
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: color || C.background2 }, line: { color: color || C.background2 }, objectName: name });
  const rondIcone = async (s, x, y, d, fondHex, Comp, nom) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fondHex }, line: { color: fondHex }, objectName: "rond-" + nom });
    const ic = SOMBRES.includes(fondHex) ? HEX.blanc : HEX.espresso;
    s.addImage({ data: await icon(Comp, ic), x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5, objectName: "icone-" + nom });
  };
  const H = HEX;

  // ---------- 1. Couverture ----------
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Introduction" });
  logoHaut(s);
  photoDroite(s, "couverture");
  s.addText("Mamo Michelangelo", { placeholder: "title" });
  s.addText([
    { text: "Benvenuti, since 1992", options: { italic: true, color: C.accent1, breakLine: true } },
    { text: "Proposition d'accompagnement Instagram, TikTok et Facebook · 2027", options: { fontSize: 16 } },
  ], { placeholder: "body" });
  s.addText("Margaux Krikorian · Community manager · 06 16 03 80 12", { x: 0.8, y: 6.35, w: 5.6, h: 0.4, fontSize: 14, color: C.accent1, margin: 0, isTextBox: true });
  s.addNotes("Présentation de l'accompagnement réseaux sociaux proposé à Mamo Michelangelo (Antibes) pour 2027.");

  // ---------- 2. Le royaume de Mamo ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Introduction" });
  s.addText("Le royaume de Mamo, depuis 1992", { placeholder: "title" });
  s.addText("Derrière les remparts d'Antibes, dans l'ancienne cave du domaine Ott, Mamo reçoit ses invités comme des amis depuis plus de trente ans. Le site le résume : « le pape de la pasta et du sourire ».",
    { x: 0.6, y: 1.5, w: 5.6, h: 1.6, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  s.addImage({ path: "photos/mamo.jpg", x: 0.6, y: 3.3, w: 2.7, h: 3.3, altText: "Mamo en salle", objectName: "photo-mamo" });
  s.addText("Mamo · mamo-michelangelo.com", { x: 0.6, y: 6.62, w: 2.7, h: 0.25, fontSize: 10, italic: true, color: C.text2, margin: 0, isTextBox: true });
  const chiffres = [["1992", "ouverture à Antibes"], ["30 ans+", "de « Guests of Mamo »"], ["3", "adresses, et Doha bientôt"]];
  chiffres.forEach(([n, l], i) => {
    s.addText([{ text: n, options: { fontSize: 28, bold: true, color: C.text2, breakLine: true } }, { text: l, options: { fontSize: 14, color: C.text1 } }],
      { x: 3.6, y: 3.3 + i * 1.12, w: 2.6, h: 1.0, margin: 0, isTextBox: true, valign: "top" });
  });
  const faits = [
    ["La table", "Raviolini et focaccia à la truffe, épaule d'agneau au feu de bois, tarte au citron géante", fa.FaUtensils, H.or],
    ["Les produits", "Truffes, tomates, burrata, cèpes : sélectionnés chez de petits producteurs d'Italie et du Sud", fa.FaLeaf, H.olive],
    ["Les invités", "De Robert De Niro à Rihanna : trois décennies de cinéma, de musique et de sport", fa.FaStar, H.terre],
    ["La marque", "Antibes, Riyadh, Saint-Barth, et Doha annoncé : un nom connu bien au-delà de la Riviera", fa.FaGlobe, H.rouge],
    ["La réservation", "En ligne avec SevenRooms, du mardi au samedi, midi et soir", fa.FaCalendarCheck, H.sable],
  ];
  for (let i = 0; i < faits.length; i++) {
    const [t, d, ic, col] = faits[i];
    const y = 1.45 + i * 1.07;
    await rondIcone(s, 6.7, y, 0.75, col, ic, "fait" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: 7.65, y: y - 0.08, w: 5.1, h: 0.95, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addNotes("Sources : mamo-michelangelo.com/antibes (histoire, cave du domaine Ott, plats, Guests of Mamo, producteurs) ; page d'accueil du site (Antibes, Riyadh, Saint-Barth, Doha « opening soon ») ; bio Instagram (mardi au samedi, midi et soir) ; Riviera Edition (Mamo, originaire de Calabre).");

  // ---------- 3. Divider diagnostic ----------
  pres.addSection({ title: "Diagnostic" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Diagnostic" });
  s.background = { color: C.text2 };
  logoHaut(s);
  photoDroite(s, "div-diagnostic");
  s.addText("Le diagnostic", { placeholder: "title" });
  s.addText("Ce que dit aujourd'hui le compte @mamomichelangelo, et ce qu'il pourrait raconter de plus", { placeholder: "body" });

  // ---------- 4. Audit ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Un compte certifié, avec une vraie notoriété", { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.4, w: 2.75, h: 5.5, rectRadius: 0.25, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "telephone" });
  s.addImage({ path: "insta.jpg", x: 0.72, y: 1.52, w: 2.51, h: 5.26, sizing: { type: "cover", w: 2.51, h: 5.26 }, altText: "Capture du profil Instagram @mamomichelangelo", objectName: "capture-profil" });
  [["52 K", "abonnés"], ["1 705", "publications"], ["2 631", "abonnements"]].forEach(([n, l], i) => {
    s.addText([{ text: n, options: { fontSize: 34, bold: true, color: C.text2, breakLine: true } }, { text: l, options: { fontSize: 14, color: C.text1 } }],
      { x: 3.85 + i * 2.95, y: 1.45, w: 2.8, h: 1.1, margin: 0, isTextBox: true });
  });
  const forces = [
    [fa.FaCircleCheck, H.or, "Un compte certifié", "Le badge bleu rassure et confirme le statut de l'adresse."],
    [fa.FaCalendarCheck, H.olive, "La réservation intégrée", "Bouton Réserver et lien SevenRooms : on réserve sans quitter Instagram."],
    [fa.FaAlignLeft, H.terre, "Une bio claire", "Ce qu'on mange, quand c'est ouvert, où c'est, comment réserver."],
    [fa.FaLink, H.sable, "Des réseaux reliés", "Threads et Facebook affichés sur le profil, stories actives."],
  ];
  for (let i = 0; i < forces.length; i++) {
    const [ic, col, t, d] = forces[i];
    const x = 3.85 + (i % 2) * 4.45, y = 2.9 + Math.floor(i / 2) * 2.0;
    carte(s, x, y, 4.25, 1.8, C.background2, "force" + i);
    await rondIcone(s, x + 0.25, y + 0.3, 0.7, col, ic, "force" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: x + 1.15, y: y + 0.2, w: 2.95, h: 1.45, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addNotes("Chiffres relevés sur le profil Instagram @mamomichelangelo (capture du 25 novembre 2026). Les statistiques internes (portée, engagement, réservations SevenRooms) seront analysées avec l'accès au compte.");

  // ---------- 5. Pistes ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Six pistes pour aller plus loin", { placeholder: "title" });
  const pistes = [
    [fa.FaComments, H.or, "Parler aussi aux Antibois", "La bio est en anglais seulement. Une version bilingue accueille aussi la clientèle locale, qui fait vivre l'hiver."],
    [fa.FaStar, H.terre, "Faire vivre la légende", "Trente ans de « Guests of Mamo » : un trésor de contenus encore peu raconté en vidéo."],
    [fa.FaUserTie, H.rouge, "Mettre Mamo à l'image", "Le patron est la marque. Ses gestes, ses mots et son accueil donnent un visage au lieu."],
    [fa.FaTiktok, H.olive, "Ouvrir TikTok", "Aucun compte TikTok trouvé à ce jour, alors que le Festival de Cannes y est très suivi chaque année."],
    [fa.FaCommentDots, H.sable, "Soigner les avis en ligne", "Tripadvisor affiche 3,6 sur 5 pour environ 880 avis, souvent sur le prix : répondre et montrer la valeur de l'assiette."],
    [fa.FaFilter, H.or, "Un compte plus sélectif", "2 631 abonnements : un tri régulier renforce l'image d'adresse confidentielle."],
  ];
  for (let i = 0; i < pistes.length; i++) {
    const [ic, col, t, d] = pistes[i];
    const x = 0.6 + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.7;
    carte(s, x, y, 3.9, 2.45, C.background2, "piste" + i);
    await rondIcone(s, x + 0.25, y + 0.25, 0.7, col, ic, "piste" + i);
    s.addText(t, { x: x + 1.1, y: y + 0.25, w: 2.65, h: 0.7, fontSize: 16, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText(d, { x: x + 0.25, y: y + 1.05, w: 3.45, h: 1.3, fontSize: 14, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addNotes("TikTok : aucun compte trouvé lors de la recherche du 25/11/2026, à confirmer. Tripadvisor : note 3,6, environ 880 avis, gamme $$$$ (tripadvisor.com). TikTok partenaire officiel du Festival de Cannes depuis 2022 (newsroom TikTok).");

  // ---------- 6. Antibes ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("À Antibes, une adresse à part", { placeholder: "title" });
  const conc = [
    ["Quinto Cielo", "Cuisine italienne et méditerranéenne sur un rooftop de Juan-les-Pins.", H.or],
    ["IL Ristorante", "Une grande salle de 140 couverts, ouverte tous les jours.", H.terre],
    ["Nacional", "Trattoria italienne citée par Gault&Millau.", H.olive],
    ["Da Vinci", "Une trattoria avec vue sur le port Vauban.", H.sable],
  ];
  conc.forEach(([t, d, col], i) => {
    const y = 1.5 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.2, w: 0.55, h: 0.55, fill: { color: col }, line: { color: col }, objectName: "pastille-" + i });
    s.addText([{ text: t, options: { bold: true, fontSize: 17, breakLine: true } }, { text: d, options: { fontSize: 15 } }],
      { x: 1.4, y, w: 5.5, h: 1.15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  });
  carte(s, 7.3, 1.5, 5.4, 5.25, C.text1, "place-mamo");
  s.addImage({ path: "photos/guests.jpg", x: 7.3, y: 1.5, w: 5.4, h: 2.1, altText: "Le mur des Guests of Mamo", objectName: "guests" });
  s.addText([
    { text: "La place de Mamo", options: { bold: true, fontSize: 22, color: C.accent1, breakLine: true } },
    { text: "La table italienne des légendes.", options: { bold: true, fontSize: 17, color: C.background1, breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Aucune autre table de la ville ne réunit trente ans de stars, un patron devenu personnage et une marque présente jusqu'au Moyen-Orient. À quelques kilomètres du Palais des Festivals, Mamo peut être l'adresse que l'on se raconte.", options: { fontSize: 15, color: C.background1 } },
  ], { x: 7.65, y: 3.85, w: 4.7, h: 2.8, margin: 0, isTextBox: true, valign: "top" });
  s.addNotes("Sources : Office de tourisme d'Antibes Juan-les-Pins (Quinto Cielo, IL Ristorante, Da Vinci) ; Gault&Millau (Nacional, Michelangelo dans la sélection d'Antibes). Le nombre d'abonnés des concurrents n'est pas publié par des sources fiables : à relever sur leurs comptes.");

  // ---------- 7. Tendances ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Ce qui fait réserver une table en 2026", { placeholder: "title" });
  const tend = [
    [fa.FaPersonWalking, H.or, "L'expérience en vidéo", "Les vidéos qui marchent montrent ce que vit le client : l'arrivée, le plat, le geste, l'ambiance."],
    [fa.FaUserTie, H.terre, "Un visage, une histoire", "Le chef ou le patron qui parle à la caméra rend l'adresse proche et unique."],
    [fa.FaBowlFood, H.olive, "L'origine dans l'assiette", "Produits locaux, origine affichée, plats à partager : la table devient un contenu à part entière."],
    [fa.FaCameraRetro, H.sable, "Un décor qui se partage", "Les lieux de caractère deviennent des scènes que les clients photographient."],
  ];
  for (let i = 0; i < tend.length; i++) {
    const [ic, col, t, d] = tend[i];
    const x = 0.6 + i * 3.08;
    carte(s, x, 1.5, 2.9, 4.3, C.background2, "tendance" + i);
    await rondIcone(s, x + 0.3, 1.8, 0.9, col, ic, "tendance" + i);
    s.addText(t, { x: x + 0.3, y: 2.95, w: 2.35, h: 0.9, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText(d, { x: x + 0.3, y: 3.9, w: 2.35, h: 1.8, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addText("Point de vigilance : la loi Évin encadre la publicité pour l'alcool. Le bar et la cave se montrent par l'ambiance et le savoir-faire, jamais par l'incitation à boire.",
    { x: 0.6, y: 6.05, w: 12.1, h: 0.7, fontSize: 14, italic: true, color: C.text2, margin: 0, isTextBox: true });
  s.addNotes("Sources : We Are Juno, « Instagram & TikTok : transformer vos visiteurs numériques en clients » ; French Tourism Embassy, « Clubs de plage 2026 : entre gastronomie, effet mode et exigence de valeur ». Sources éditoriales, sans chiffres d'engagement publiés.");

  // ---------- 8. Divider stratégie ----------
  pres.addSection({ title: "Stratégie" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Stratégie" });
  logoHaut(s);
  photoDroite(s, "div-strategie");
  s.addText("La stratégie", { placeholder: "title" });
  s.addText("Faire vivre la légende de Mamo en ligne, et remplir la salle toute l'année", { placeholder: "body" });

  // ---------- 9. Objectifs ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Trois objectifs pour 2027", { placeholder: "title" });
  const obj = [
    ["01", "Remplir les tables, du mardi au samedi", "Chaque contenu mène à SevenRooms. Les stories annoncent la truffe du jour, les soirées et les tables encore libres.", H.or],
    ["02", "Faire rayonner la légende", "Un récit cohérent, en français et en anglais, sur Instagram, TikTok et Facebook, à la hauteur d'une marque internationale.", H.terre],
    ["03", "Fidéliser toute l'année", "Les Antibois et les habitués l'hiver, les visiteurs l'été : un rythme et des messages pour chacun.", H.olive],
  ];
  obj.forEach(([n, t, d, col], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.OVAL, { x, y: 1.6, w: 1.2, h: 1.2, fill: { color: col }, line: { color: col }, objectName: "num-" + i });
    s.addText(n, { x, y: 1.6, w: 1.2, h: 1.2, fontSize: 30, bold: true, color: i === 2 ? C.background1 : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x, y: 3.05, w: 3.8, h: 0.9, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText(d, { x, y: 3.95, w: 3.8, h: 1.6, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  carte(s, 0.6, 5.65, 12.1, 1.0, C.background2, "indicateurs");
  s.addText([{ text: "Ce que je mesure chaque mois : ", options: { bold: true } }, { text: "les réservations venues d'Instagram, les messages reçus, la portée, les nouveaux abonnés, les vues des vidéos et la note des avis." }],
    { x: 0.9, y: 5.7, w: 11.5, h: 0.9, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 10. Piliers ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Cinq piliers pour tout raconter", { placeholder: "title" });
  const pil = [
    ["p-table", H.or, "La table", "La truffe, le feu de bois, les plats signature"],
    ["p-mamo", H.rouge, "Mamo", "Le patron, son accueil, ses histoires"],
    ["p-cave", H.terre, "La cave", "Les vieilles pierres, le décor, l'intimité du lieu"],
    ["p-legendes", H.olive, "Les légendes", "Trente ans de « Guests of Mamo »"],
    ["p-dolce", H.sable, "La dolce vita", "Le bar, la terrasse, les soirées"],
  ];
  pil.forEach(([img, col, t, d], i) => {
    const x = 0.6 + i * 2.47;
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 1.55, w: 1.55, h: 1.55, fill: { color: col }, line: { color: col }, objectName: "anneau-pilier" + i });
    s.addImage({ path: "photos/" + img + ".jpg", x: x + 0.43, y: 1.63, w: 1.39, h: 1.39, rounding: true, altText: t, objectName: "photo-pilier" + i });
    s.addText(t, { x, y: 3.3, w: 2.25, h: 0.6, fontSize: 20, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x, y: 3.95, w: 2.25, h: 1.3, fontSize: 15, color: C.text1, align: "center", margin: 0, isTextBox: true, valign: "top" });
  });
  carte(s, 0.6, 5.5, 12.1, 1.15, C.background2, "ton");
  s.addText([{ text: "Le ton : ", options: { bold: true } }, { text: "chaleureux, élégant, généreux, bilingue. On vouvoie, comme on reçoit un invité de marque, avec la jovialité de Mamo. Le crème et l'or du logo signent chaque visuel." }],
    { x: 0.9, y: 5.6, w: 11.5, h: 0.95, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 11. Bio & réservation ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Un profil bilingue, qui mène à la table", { placeholder: "title" });
  carte(s, 0.6, 1.5, 5.6, 3.3, C.text1, "bio");
  s.addText([
    { text: "La bio proposée", options: { bold: true, fontSize: 14, color: C.accent1, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "🍝 La cucina di Mamo, since 1992", options: { breakLine: true } },
    { text: "⭐ Guests of Mamo · Vieil Antibes", options: { breakLine: true } },
    { text: "🕯️ Mar.–sam. · Tue–Sat · lunch & dinner", options: { breakLine: true } },
    { text: "📲 Réservez · Book your table 👇", options: {} },
  ], { x: 0.95, y: 1.75, w: 5.0, h: 2.9, fontSize: 19, color: C.background1, margin: 0, isTextBox: true, valign: "top" });
  carte(s, 0.6, 5.05, 5.6, 1.6, C.background2, "liens");
  s.addText([
    { text: "Les liens du profil", options: { bold: true, fontSize: 16, breakLine: true } },
    { text: "Réserver (SevenRooms)  ·  La carte  ·  Événements privés", options: { fontSize: 15 } },
  ], { x: 0.9, y: 5.2, w: 5.0, h: 1.3, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  const etapes = [
    [fa.FaLanguage, H.or, "Deux langues, un seul compte", "Légendes en français et en anglais, sous-titres sur toutes les vidéos."],
    [fa.FaCalendarCheck, H.olive, "SevenRooms partout", "Bouton Réserver, lien en bio et sticker dans les stories : un seul chemin, mesurable."],
    [fa.FaStar, H.terre, "Des stories à la une utiles", "Guests, La carte, Mamo, La cave, Événements, Réserver : les réponses aux questions de chaque jour."],
  ];
  for (let i = 0; i < etapes.length; i++) {
    const [ic, col, t, d] = etapes[i];
    const y = 1.5 + i * 1.75;
    await rondIcone(s, 6.7, y + 0.2, 0.8, col, ic, "etape" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 17, breakLine: true } }, { text: d, options: { fontSize: 15 } }],
      { x: 7.7, y, w: 5.0, h: 1.4, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addNotes("Bio à valider avec Mamo et son équipe. Les horaires viennent de la bio actuelle (« Open Tuesday to Saturday for lunch & dinner »).");

  // ---------- 12. Divider contenus ----------
  pres.addSection({ title: "Contenus" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Contenus" });
  s.background = { color: C.text2 };
  logoHaut(s);
  photoDroite(s, "div-contenus");
  s.addText("Les contenus", { placeholder: "title" });
  s.addText("Des formats pensés pour chaque réseau, au rythme d'Antibes", { placeholder: "body" });

  // ---------- 13. Formats ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Un format pour chaque envie", { placeholder: "title" });
  const formats = [
    [fa.FaFilm, H.rouge, "Réels et TikTok", ["Mamo en cuisine, en 15 secondes", "La truffe râpée à table", "Le service du soir", "Une légende, une anecdote"]],
    [fa.FaImages, H.or, "Carrousels", ["Guests of Mamo : 30 ans en images", "La carte, plat par plat", "Les producteurs de Mamo", "Le Vieil Antibes vu par Mamo"]],
    [fa.FaMobileScreen, H.olive, "Stories", ["La truffe du jour", "Ce soir chez Mamo", "Quiz : qui s'est assis ici ?", "Les coulisses en direct"]],
  ];
  for (let i = 0; i < formats.length; i++) {
    const [ic, col, t, items] = formats[i];
    const x = 0.6 + i * 4.1;
    carte(s, x, 1.5, 3.9, 4.45, C.background2, "format" + i);
    await rondIcone(s, x + 0.3, 1.8, 0.9, col, ic, "format" + i);
    s.addText(t, { x: x + 1.4, y: 1.8, w: 2.3, h: 0.9, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText(items.map((it, k) => ({ text: it, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.95, w: 3.35, h: 2.85, fontSize: 16, color: C.text1, paraSpaceAfter: 10, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addText("Chaque vidéo est livrée en deux versions, Instagram et TikTok, sous-titrée en français et en anglais.",
    { x: 0.6, y: 6.15, w: 12.1, h: 0.55, fontSize: 15, italic: true, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 14. Exemples ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Trois idées prêtes à tourner", { placeholder: "title" });
  const ex = [
    ["Réel", "Le pape de la pasta", "Mamo dresse une assiette et raconte en une phrase pourquoi il cuisine ainsi depuis 1992. Sous-titres FR et EN.", H.rouge, "ex-reel"],
    ["Carrousel", "Guests of Mamo", "Une photo d'archive par slide, une anecdote par invité. Dernière image : « Votre table vous attend ».", H.or, "ex-carrousel"],
    ["Story", "Ce soir chez Mamo", "Chaque jour d'ouverture : la suggestion du chef, l'ambiance de la salle et le bouton Réserver.", H.olive, "ex-story"],
  ];
  ex.forEach(([type, t, d, col, img], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.47, y: 1.37, w: 2.96, h: 4.06, rectRadius: 0.22, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "cadre-" + i });
    s.addImage({ path: "photos/" + img + ".jpg", x: x + 0.55, y: 1.45, w: 2.8, h: 3.9, altText: "Exemple " + type, objectName: "maquette-" + i });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.85, y: 1.65, w: 2.2, h: 0.4, rectRadius: 0.2, fill: { color: col }, line: { color: col }, objectName: "etiquette-" + i });
    s.addText(type.toUpperCase(), { x: x + 0.85, y: 1.65, w: 2.2, h: 0.4, fontSize: 12, bold: true, charSpacing: 3, color: SOMBRES.includes(col) ? C.background1 : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.8, y: 4.25, w: 2.3, h: 0.9, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: "titre-maquette-" + i });
    s.addText(t, { x: x + 0.8, y: 4.25, w: 2.3, h: 0.9, fontSize: 17, italic: true, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(d, { x, y: 5.6, w: 3.9, h: 1.2, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addNotes("Photos des maquettes : mamo-michelangelo.com. Elles illustrent l'idée ; les vrais contenus seront tournés sur place.");

  // ---------- 15. L'année ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Une année au rythme d'Antibes", { placeholder: "title" });
  const annee = [
    ["Janvier → mars", "L'hiver", "Les Antibois et les habitués : la carte d'hiver, la truffe, les coulisses, les archives.", H.olive],
    ["Avril → mai", "Le Festival", "Le Festival de Cannes : les légendes, les soirées, l'effervescence de la Croisette.", H.or],
    ["Juin → août", "L'été", "La terrasse, les visiteurs du monde entier, des contenus en anglais chaque jour.", H.terre],
    ["Septembre → octobre", "L'arrière-saison", "La lumière d'automne, les produits de saison, les cèpes et la truffe blanche.", H.rouge],
    ["Novembre → décembre", "Les fêtes", "Les réveillons, les privatisations et les cadeaux : on remplit les grandes tables.", H.sable],
  ];
  s.addShape(pres.shapes.LINE, { x: 0.9, y: 2.75, w: 11.5, h: 0, line: { color: C.text2, width: 2 }, objectName: "frise" });
  annee.forEach(([p, t, d, col], i) => {
    const x = 0.6 + i * 2.47;
    s.addShape(pres.shapes.OVAL, { x: x + 0.85, y: 2.45, w: 0.6, h: 0.6, fill: { color: col }, line: { color: col }, objectName: "etape-annee-" + i });
    s.addText(p, { x, y: 1.85, w: 2.3, h: 0.4, fontSize: 14, bold: true, color: C.text2, align: "center", margin: 0, isTextBox: true });
    s.addText(t, { x, y: 3.3, w: 2.3, h: 0.5, fontSize: 19, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.05, y: 3.95, w: 2.2, h: 2.1, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addText("Les dates exactes des temps forts (Festival de Cannes, Jazz à Juan, fermetures) seront calées avec vous dans le calendrier éditorial de chaque mois.",
    { x: 0.6, y: 6.15, w: 12.1, h: 0.6, fontSize: 14, italic: true, color: C.text2, margin: 0, isTextBox: true });

  // ---------- 16. Divider offre ----------
  pres.addSection({ title: "Offre" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Offre" });
  logoHaut(s);
  photoDroite(s, "div-offre");
  s.addText("Mon accompagnement", { placeholder: "title" });
  s.addText("Une formule à la hauteur d'une adresse de légende", { placeholder: "body" });

  // ---------- 17. Offre ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("Deux formules, au choix", { placeholder: "title" });
  const offres = [
    ["Visibilité", "pour aller chercher de nouveaux clients", "1 290 €", "par mois", H.sable, [
      "Instagram, TikTok et Facebook",
      "16 publications et 20 stories par mois",
      "6 réels et TikTok par mois, montés",
      "Une campagne publicitaire Meta par mois (budget à part)",
      "Fiche Google : photos, posts et réponses aux avis",
      "Réponses aux messages et commentaires 6 j/7",
      "Rapport et point mensuel d'une heure",
    ], false],
    ["Prestige", "recommandée · pour remplir la salle mois après mois", "1 490 €", "par mois", H.or, [
      "Toute la formule Visibilité",
      "Une demi-journée photo et vidéo sur place à chaque saison",
      "Plats, salle, cave, équipe : photos retouchées et cédées",
      "Vous n'avez plus rien à fournir",
      "Les temps forts couverts : Festival, été, fêtes",
    ], true],
  ];
  offres.forEach(([nom, sous, prix, per, col, items, reco], i) => {
    const x = 0.6 + i * 6.15;
    carte(s, x, 1.45, 5.95, 5.3, reco ? C.text1 : C.background2, "offre" + i);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.3, y: 1.7, w: 5.35, h: 1.45, rectRadius: 0.08, fill: { color: col }, line: { color: col }, objectName: "entete-offre" + i });
    s.addText([{ text: nom, options: { bold: true, fontSize: 24, breakLine: true } }, { text: sous, options: { fontSize: 13 } }],
      { x: x + 0.55, y: 1.8, w: 3.2, h: 1.25, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText([{ text: prix, options: { bold: true, fontSize: 30, breakLine: true } }, { text: per, options: { fontSize: 13 } }],
      { x: x + 3.6, y: 1.8, w: 1.9, h: 1.25, color: C.text1, align: "right", margin: 0, isTextBox: true, valign: "middle" });
    s.addText(items.map((it, k) => ({ text: it, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.45, y: 3.4, w: 5.1, h: 3.2, fontSize: 16, color: reco ? C.background1 : C.text1, paraSpaceAfter: 6, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addNotes("Tarifs repris de la grille de Margaux Krikorian (valable jusqu'au 30/06/2027). TVA non applicable, article 293 B du CGI. Budget publicitaire réglé directement par l'établissement à Meta (conseillé : 150 à 300 € par mois).");

  // ---------- 18. Année en clair ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("L'année complète, en clair", { placeholder: "title" });
  carte(s, 0.6, 1.5, 5.4, 4.6, C.text1, "total");
  s.addText([
    { text: "Formule Prestige × 12 mois", options: { breakLine: true } },
    { text: " ", options: { fontSize: 10, breakLine: true } },
    { text: "17 880 €", options: { bold: true, fontSize: 48, color: C.accent1, breakLine: true } },
    { text: "pour l'année, soit 1 490 € par mois", options: { fontSize: 15, breakLine: true } },
    { text: "TVA non applicable, article 293 B du CGI", options: { fontSize: 13 } },
  ], { x: 1.0, y: 1.85, w: 4.7, h: 3.4, fontSize: 19, color: C.background1, margin: 0, isTextBox: true, valign: "top" });
  s.addText("Mise en place offerte (audit, charte, profils) pour un engagement de 6 mois", { x: 1.0, y: 5.1, w: 4.7, h: 0.8, fontSize: 14, italic: true, color: C.background2, margin: 0, isTextBox: true });
  const opts = [
    [fa.FaCamera, H.or, "Séance photo supplémentaire", "600 € la demi-journée"],
    [fa.FaFilm, H.rouge, "Réel supplémentaire", "90 € le réel"],
    [fa.FaChampagneGlasses, H.terre, "Couverture d'un événement", "Soirée, privatisation, Festival : sur devis"],
    [fa.FaHandshake, H.olive, "Conditions", "Engagement de 3 mois, puis sans engagement. Facturation mensuelle, paiement à 15 jours. Chaque contenu est validé par vous."],
  ];
  for (let i = 0; i < opts.length; i++) {
    const [ic, col, t, d] = opts[i];
    const y = 1.5 + i * 1.2;
    await rondIcone(s, 6.5, y + 0.15, 0.75, col, ic, "option" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 17, breakLine: true } }, { text: d, options: { fontSize: 15 } }],
      { x: 7.45, y, w: 5.25, h: 1.1, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addNotes("Calcul : 12 × 1 490 = 17 880 €. Avec la formule Visibilité : 12 × 1 290 = 15 480 €.");

  // ---------- 19. Méthode ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("Comment nous travaillerons", { placeholder: "title" });
  const meth = [
    ["Semaine 1", "Rencontre au restaurant, accès aux comptes, audit des statistiques et des avis"],
    ["Semaine 2", "Charte réseaux, bio bilingue, stories à la une, liens SevenRooms"],
    ["Semaine 3", "Premier calendrier éditorial et première séance photo et vidéo"],
    ["Chaque mois", "Calendrier validé par vous, publications, réponses, rapport et point d'une heure"],
  ];
  meth.forEach(([t, d], i) => {
    const x = 0.6 + i * 3.08;
    const col = [H.or, H.rouge, H.terre, H.olive][i];
    s.addShape(pres.shapes.OVAL, { x: x + 0.95, y: 1.6, w: 1.0, h: 1.0, fill: { color: col }, line: { color: col }, objectName: "methode-" + i });
    s.addText(String(i + 1), { x: x + 0.95, y: 1.6, w: 1.0, h: 1.0, fontSize: 28, bold: true, color: SOMBRES.includes(col) ? C.background1 : C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.05, y: 2.1, w: 1.95, h: 0, line: { color: C.text2, width: 2, dashType: "dash" }, objectName: "fleche-" + i });
    s.addText(t, { x, y: 2.85, w: 2.9, h: 0.5, fontSize: 18, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.1, y: 3.4, w: 2.7, h: 1.8, fontSize: 16, color: C.text1, align: "center", margin: 0, isTextBox: true, valign: "top" });
  });
  carte(s, 0.6, 5.3, 12.1, 1.3, C.background2, "engagement");
  s.addText([{ text: "Mon engagement : ", options: { bold: true } }, { text: "rien n'est publié sans votre accord, les vidéos sont montées pour Instagram et pour TikTok, et vous gardez la main sur vos comptes à tout moment." }],
    { x: 0.9, y: 5.4, w: 11.5, h: 1.1, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 20. Fin ----------
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Offre" });
  logoHaut(s);
  photoDroite(s, "fin");
  s.addText("Racontons ensemble la légende de Mamo", { placeholder: "title" });
  s.addText([
    { text: "Prochaine étape : un rendez-vous au restaurant pour caler 2027 ensemble.", options: { breakLine: true } },
    { text: "Margaux Krikorian · Community manager", options: { color: C.accent1, breakLine: true } },
    { text: "06 16 03 80 12", options: { color: C.accent1 } },
  ], { placeholder: "body" });
  s.addNotes("Sources : mamo-michelangelo.com ; Riviera Edition ; Tripadvisor ; Office de tourisme d'Antibes Juan-les-Pins ; Gault&Millau ; We Are Juno ; French Tourism Embassy ; TikTok Newsroom (Festival de Cannes) ; capture du profil Instagram @mamomichelangelo du 25/11/2026.");

  await pres.writeFile({ fileName: "Mamo-Michelangelo-proposition.pptx" });
  await applyTheme("Mamo-Michelangelo-proposition.pptx", THEME);
  console.log("ok");
})().catch(e => { console.error(e); process.exit(1); });
