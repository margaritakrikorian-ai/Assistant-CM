const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require("/root/.claude/skills/synced/b9a3ddc6-8a95-409a-b3ac-b8eea1a139e3_90ee0b07-47bf-455b-ac9a-75d6dee4c777/pptx/scripts/apply_theme.js");

const HEX = {
  nuit: "0F1B2D", blanc: "FFFFFF", vert: "1E5E4A", sable: "F6EEE4",
  saumon: "DFAB8C", feuille: "50A678", rose: "E29FB1", lagon: "5ABEC1", soleil: "EFCD7A",
};
const THEME = {
  name: "Moorea Happiness",
  headFontFace: "Bookman Old Style",
  bodyFontFace: "Calibri",
  colors: {
    dk1: HEX.nuit, lt1: HEX.blanc, dk2: HEX.vert, lt2: HEX.sable,
    accent1: HEX.saumon, accent2: HEX.feuille, accent3: HEX.rose, accent4: HEX.lagon, accent5: HEX.soleil, accent6: HEX.vert,
    hlink: HEX.vert, folHlink: HEX.vert,
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
  pres.title = "Moorea Plage · Proposition réseaux sociaux";
  pres.author = "Margaux Krikorian";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const W = 13.333;

  const FOOT = "Moorea Plage · Proposition d'accompagnement réseaux sociaux · Margaux Krikorian";
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
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.05, w: 5.4, h: 1.6, fontSize: 18, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });

  // motif : les bulles colorées des stories à la une de Moorea
  const bulles = (s, x, y, d) => {
    [C.accent2, C.accent3, C.accent4, C.accent5].forEach((c, i) =>
      s.addShape(pres.shapes.OVAL, { x: x + i * (d * 1.18), y, w: d, h: d, fill: { color: c }, line: { color: c }, objectName: "bulle-" + i }));
  };
  const photoDroite = (s, nom) => {
    s.addImage({ path: "photos/" + nom + ".jpg", x: 6.667, y: 0, w: 6.667, h: 7.5, altText: "Photo de Moorea Plage", objectName: "photo-" + nom });
    s.addText("Photo : mooreaplage.fr", { x: 6.9, y: 7.05, w: 6.2, h: 0.3, fontSize: 10, color: C.background1, align: "right", margin: 0, isTextBox: true, objectName: "credit-" + nom });
  };
  const carte = (s, x, y, w, h, color, name) =>
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: color || C.background2 }, line: { color: color || C.background2 }, objectName: name });
  const rondIcone = async (s, x, y, d, fond, Comp, nom) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fond }, line: { color: fond }, objectName: "rond-" + nom });
    s.addImage({ data: await icon(Comp, HEX.nuit), x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5, objectName: "icone-" + nom });
  };

  // ---------- 1. Couverture ----------
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Introduction" });
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "couverture");
  s.addText("Moorea Plage", { placeholder: "title" });
  s.addText([
    { text: "Happiness providers since 1952", options: { italic: true, breakLine: true } },
    { text: "Proposition d'accompagnement Instagram, TikTok et Facebook · saison 2027", options: { fontSize: 16 } },
  ], { placeholder: "body" });
  s.addText("Margaux Krikorian · Community manager · 06 16 03 80 12", { x: 0.8, y: 6.5, w: 5.6, h: 0.4, fontSize: 14, color: C.accent5, margin: 0, isTextBox: true });
  s.addNotes("Présentation de l'accompagnement réseaux sociaux proposé à Moorea Plage pour la saison 2027.");

  // ---------- 2. Ce que j'ai compris ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Introduction" });
  s.addText("Moorea, une famille et une plage depuis 1952", { placeholder: "title" });
  s.addText("Une paillote en bambou, une vingtaine de matelas et deux parasols : c'est ainsi que Moorea commence en 1952. Aujourd'hui, Christophe Coutal et son équipe perpétuent l'esprit de la maison : simplicité, authenticité et convivialité.",
    { x: 0.6, y: 1.5, w: 5.6, h: 1.6, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  const faits = [
    ["La plage", "Beds baldaquin, beds bord de mer et transats face à Pampelonne", fa.FaUmbrellaBeach, C.accent4],
    ["Le restaurant", "Cuisine méditerranéenne aux accents asiatiques, 7 j/7 de 12 h à 17 h", fa.FaUtensils, C.accent1],
    ["Claudy's Bar", "Cocktails, jus frais, DJ et musique live jusqu'au coucher du soleil", fa.FaMusic, C.accent3],
    ["Le village", "Boutiques en bord de plage, coiffeur, massage, ostéopathe", fa.FaBagShopping, C.accent5],
    ["L'accès", "Parking privé, ponton et navette pour les bateaux", fa.FaAnchor, C.accent2],
  ];
  for (let i = 0; i < faits.length; i++) {
    const [t, d, ic, col] = faits[i];
    const y = 1.45 + i * 1.07;
    await rondIcone(s, 6.7, y, 0.75, col, ic, "fait" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: 7.65, y: y - 0.05, w: 5.1, h: 0.9, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addImage({ path: "photos/archive.jpg", x: 0.6, y: 3.3, w: 2.7, h: 3.3, altText: "Photo d'archive de Moorea Plage", objectName: "archive" });
  s.addText("Archives Moorea · mooreaplage.fr", { x: 0.6, y: 6.62, w: 2.7, h: 0.25, fontSize: 10, italic: true, color: C.text2, margin: 0, isTextBox: true });
  const chiffres = [["1952", "année de création"], ["74 ans", "d'histoire en 2026"], ["2", "générations Coutal à la barre"]];
  chiffres.forEach(([n, l], i) => {
    s.addText([{ text: n, options: { fontFace: "Bookman Old Style", fontSize: 28, bold: true, color: C.text2, breakLine: true } }, { text: l, options: { fontSize: 14, color: C.text1 } }],
      { x: 3.6, y: 3.3 + i * 1.12, w: 2.6, h: 1.0, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addNotes("Sources : mooreaplage.fr (histoire, plage, restaurant, bar, contact) ; SO Edition (Christophe Coutal, reprise depuis 1993, père aux commandes en 1980).");

  // ---------- 3. Divider diagnostic ----------
  pres.addSection({ title: "Diagnostic" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Diagnostic" });
  s.background = { color: C.text2 };
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "div-diagnostic");
  s.addText("Le diagnostic", { placeholder: "title" });
  s.addText("Ce que dit aujourd'hui le compte @moorea_plage, et ce qu'il pourrait dire de plus", { placeholder: "body" });

  // ---------- 4. Audit du profil ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Un compte déjà aimé, avec une vraie signature", { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.4, w: 2.75, h: 5.5, rectRadius: 0.25, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "telephone" });
  s.addImage({ path: "insta.jpg", x: 0.72, y: 1.52, w: 2.51, h: 5.26, sizing: { type: "cover", w: 2.51, h: 5.26 }, altText: "Capture du profil Instagram @moorea_plage", objectName: "capture-profil" });
  const stats = [["34,5 K", "abonnés"], ["1 588", "publications"], ["405", "abonnements"]];
  stats.forEach(([n, l], i) => {
    s.addText([{ text: n, options: { fontFace: "Bookman Old Style", fontSize: 34, bold: true, color: C.text2, breakLine: true } }, { text: l, options: { fontSize: 14, color: C.text1 } }],
      { x: 3.85 + i * 2.95, y: 1.45, w: 2.8, h: 1.1, margin: 0, isTextBox: true });
  });
  const forces = [
    [fa.FaPalette, C.accent3, "Une identité illustrée unique", "Logo à l'hibiscus, couleurs pastel, palmiers dessinés : on reconnaît Moorea au premier coup d'œil."],
    [fa.FaPeopleGroup, C.accent2, "Des coulisses authentiques", "Le ratissage du sable, l'installation des beds : la vraie vie de la plage, sans artifice."],
    [fa.FaPhone, C.accent4, "Un bouton Appeler", "Le profil professionnel permet déjà de joindre la plage en un geste."],
    [fa.FaHeart, C.accent5, "Une histoire forte", "« Plage mythique depuis 1952 » : l'ancienneté est affichée dès la bio."],
  ];
  for (let i = 0; i < forces.length; i++) {
    const [ic, col, t, d] = forces[i];
    const x = 3.85 + (i % 2) * 4.45, y = 2.9 + Math.floor(i / 2) * 2.0;
    carte(s, x, y, 4.25, 1.8, C.background2, "force" + i);
    await rondIcone(s, x + 0.25, y + 0.3, 0.7, col, ic, "force" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: x + 1.15, y: y + 0.2, w: 2.95, h: 1.45, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addNotes("Chiffres relevés sur le profil Instagram @moorea_plage (capture du 25 novembre 2026). Les statistiques internes (portée, taux d'engagement) seront analysées avec l'accès au compte.");

  // ---------- 5. Pistes de progrès ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Six pistes pour aller plus loin", { placeholder: "title" });
  const pistes = [
    [fa.FaCalendarCheck, C.accent1, "Réserver en un geste", "Aujourd'hui, la réservation se fait uniquement par téléphone, et le lien de la bio passe par une page intermédiaire."],
    [fa.FaPenNib, C.accent3, "Une bio qui donne envie d'agir", "La bio dit d'où vient Moorea, mais pas quoi y faire ni comment réserver. La devise « Happiness providers » n'y figure pas."],
    [fa.FaSnowflake, C.accent4, "Garder le lien l'hiver", "La plage ferme l'hiver : c'est le moment de raconter l'histoire et de préparer la réouverture avec la communauté."],
    [fa.FaTiktok, C.accent2, "Ouvrir TikTok", "Aucun compte TikTok trouvé, alors que les vidéos de plage de Pampelonne y circulent beaucoup."],
    [fa.FaGlobe, C.accent5, "Parler aussi anglais", "La clientèle est internationale : légendes bilingues et sous-titres sur les vidéos."],
    [fa.FaStar, C.accent1, "Compléter les stories à la une", "Plage, Vous, Restaurant, L'équipe : il manque Réserver, Bar, Boutiques et Bien-être."],
  ];
  for (let i = 0; i < pistes.length; i++) {
    const [ic, col, t, d] = pistes[i];
    const x = 0.6 + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.7;
    carte(s, x, y, 3.9, 2.45, C.background2, "piste" + i);
    await rondIcone(s, x + 0.25, y + 0.25, 0.7, col, ic, "piste" + i);
    s.addText(t, { x: x + 1.1, y: y + 0.25, w: 2.6, h: 0.7, fontSize: 16, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText(d, { x: x + 0.25, y: y + 1.1, w: 3.45, h: 1.2, fontSize: 14, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addNotes("Réservation par téléphone uniquement d'après mooreaplage.fr/contact (plage 04 94 97 06 09, restaurant 04 94 97 18 17). TikTok : aucun compte trouvé lors de la recherche du 25/11/2026, à confirmer avec l'équipe.");

  // ---------- 6. Pampelonne ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Sur Pampelonne, chaque plage a son récit", { placeholder: "title" });
  const conc = [
    ["Club 55", "Né en 1955, le club héritage de la plage : nappes provençales et paniers de légumes en vedette.", C.accent4],
    ["Nikki Beach", "La plage de la fête, autour de la piscine.", C.accent3],
    ["Shellona", "La plage de la musique électronique.", C.accent5],
    ["Les maisons de mode", "Des marques de luxe s'installent sur les plages le temps d'un été, comme Gucci à La Rose des Vents.", C.accent2],
  ];
  conc.forEach(([t, d, col], i) => {
    const y = 1.5 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.15, w: 0.55, h: 0.55, fill: { color: col }, line: { color: col }, objectName: "pastille-" + i });
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
      { x: 1.4, y, w: 5.4, h: 1.1, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  });
  carte(s, 7.3, 1.5, 5.4, 5.25, C.text2, "place-moorea");
  s.addImage({ path: "photos/m-geant.jpg", x: 7.3, y: 1.5, w: 5.4, h: 1.9, altText: "Le grand M de Moorea Plage", objectName: "m-geant" });
  s.addText([
    { text: "La place de Moorea", options: { fontFace: "Bookman Old Style", bold: true, fontSize: 20, color: C.accent5, breakLine: true } },
    { text: "La plage d'origine, joyeuse et familiale.", options: { bold: true, fontSize: 16, color: C.background1, breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Créée en 1952, trois ans avant le Club 55, tenue par la même famille depuis plus de quarante ans : Moorea peut incarner le bonheur simple de Pampelonne, où l'on vient en famille et où l'on revient chaque été.", options: { fontSize: 14, color: C.background1 } },
  ], { x: 7.65, y: 3.6, w: 4.7, h: 3.05, margin: 0, isTextBox: true, valign: "top" });
  s.addNotes("Sources : St Tropez House (Club 55, 1955) ; French Riviera Luxury Villas, guide 2026 (Club 55, Shellona, Nikki Beach) ; The Taste Edit (Club 55 sur Instagram) ; Acumen et Elite Traveler (plages des maisons de mode, Gucci à La Rose des Vents). Nombre d'abonnés des concurrents non publié par des sources fiables : à relever directement sur leurs comptes.");

  // ---------- 7. Tendances ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Diagnostic" });
  s.addText("Ce qui fait réserver une plage en 2026", { placeholder: "title" });
  const tend = [
    [fa.FaCameraRetro, C.accent3, "Un décor qui se partage", "Le beach club est devenu un lieu hybride : restaurant, scène sociale et décor que l'on photographie."],
    [fa.FaPersonWalking, C.accent4, "Le parcours du client en vidéo", "Les vidéos qui marchent montrent l'expérience vécue : l'arrivée, le bed, le plat, le coucher du soleil."],
    [fa.FaBowlFood, C.accent1, "Des assiettes à partager", "Plats photogéniques, produits locaux et origine affichée : la table devient un contenu à part entière."],
    [fa.FaSun, C.accent5, "De la plage au coucher du soleil", "Les contenus « de la journée au sunset » portent l'envie de rester jusqu'au soir."],
  ];
  for (let i = 0; i < tend.length; i++) {
    const [ic, col, t, d] = tend[i];
    const x = 0.6 + i * 3.08;
    carte(s, x, 1.5, 2.9, 4.3, C.background2, "tendance" + i);
    await rondIcone(s, x + 0.3, 1.8, 0.9, col, ic, "tendance" + i);
    s.addText(t, { x: x + 0.3, y: 2.95, w: 2.35, h: 0.9, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText(d, { x: x + 0.3, y: 3.9, w: 2.35, h: 1.8, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  }
  s.addText("Point de vigilance : la loi Évin encadre la publicité pour l'alcool. Les contenus du bar mettent en avant l'ambiance, les jus et les cocktails sans alcool, jamais l'incitation à boire.",
    { x: 0.6, y: 6.1, w: 12.1, h: 0.7, fontSize: 13, italic: true, color: C.text2, margin: 0, isTextBox: true });
  s.addNotes("Sources : French Tourism Embassy, « Clubs de plage 2026 » ; We Are Juno, « Instagram & TikTok : transformer vos visiteurs numériques en clients » ; Acumen, « Beach clubs 2026 ». Ces sources sont éditoriales : pas de chiffres d'engagement publiés.");

  // ---------- 8. Divider stratégie ----------
  pres.addSection({ title: "Stratégie" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Stratégie" });
  s.background = { color: C.text1 };
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "div-strategie");
  s.addText("La stratégie", { placeholder: "title" });
  s.addText("Faire ressentir en ligne ce que les habitués vivent sur place, et le transformer en réservations", { placeholder: "body" });

  // ---------- 9. Objectifs ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Trois objectifs pour la saison 2027", { placeholder: "title" });
  const obj = [
    ["01", "Remplir les beds et les tables", "Un chemin de réservation en un geste depuis Instagram et TikTok, et des stories qui annoncent chaque jour les disponibilités et la carte.", C.accent4],
    ["02", "Faire rayonner la marque", "Un récit cohérent sur tous les réseaux, en français et en anglais, pour toucher la clientèle internationale avant même son arrivée.", C.accent1],
    ["03", "Garder la communauté toute l'année", "Un rythme allégé l'hiver : archives, coulisses, compte à rebours avant la réouverture. On ne repart jamais de zéro au printemps.", C.accent2],
  ];
  obj.forEach(([n, t, d, col], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.OVAL, { x, y: 1.6, w: 1.2, h: 1.2, fill: { color: col }, line: { color: col }, objectName: "num-" + i });
    s.addText(n, { x, y: 1.6, w: 1.2, h: 1.2, fontFace: "Bookman Old Style", fontSize: 30, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x, y: 3.05, w: 3.8, h: 0.9, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText(d, { x, y: 3.95, w: 3.8, h: 1.6, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  carte(s, 0.6, 5.65, 12.1, 1.0, C.background2, "indicateurs");
  s.addText([{ text: "Ce que je mesure chaque mois : ", options: { bold: true } }, { text: "les clics sur les liens de réservation, les messages reçus, la portée, les nouveaux abonnés et les vues des vidéos." }],
    { x: 0.9, y: 5.7, w: 11.5, h: 0.9, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 10. Piliers ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Cinq piliers pour tout raconter", { placeholder: "title" });
  const pil = [
    ["p-plage", C.accent4, "La plage", "La mer, la lumière, les beds au petit matin"],
    ["p-table", C.accent1, "La table", "Les chefs, les plats à partager, la carte du jour"],
    ["p-gens", C.accent3, "Les gens", "Les « happiness providers », Claudy, les habitués"],
    ["p-histoire", C.accent5, "L'histoire", "1952, les archives, la famille, les anecdotes"],
    ["p-moments", C.accent2, "Les moments", "Sunset, DJ, live, boutiques, bien-être"],
  ];
  for (let i = 0; i < pil.length; i++) {
    const [ic, col, t, d] = pil[i];
    const x = 0.6 + i * 2.47;
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 1.55, w: 1.55, h: 1.55, fill: { color: col }, line: { color: col }, objectName: "anneau-pilier" + i });
    s.addImage({ path: "photos/" + ic + ".jpg", x: x + 0.43, y: 1.63, w: 1.39, h: 1.39, rounding: true, altText: t, objectName: "photo-pilier" + i });
    s.addText(t, { x, y: 3.25, w: 2.25, h: 0.6, fontSize: 20, bold: true, fontFace: "Bookman Old Style", color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x, y: 3.9, w: 2.25, h: 1.3, fontSize: 14, color: C.text1, align: "center", margin: 0, isTextBox: true, valign: "top" });
  }
  carte(s, 0.6, 5.5, 12.1, 1.15, C.background2, "ton");
  s.addText([{ text: "Le ton : ", options: { bold: true } }, { text: "chaleureux, solaire, un brin d'humour, bilingue. On tutoie la communauté, comme on accueille un habitué. Les illustrations maison restent la signature de chaque visuel." }],
    { x: 0.9, y: 5.6, w: 11.5, h: 0.95, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 11. Bio et réservation ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Stratégie" });
  s.addText("Réserver en un geste, depuis le profil", { placeholder: "title" });
  carte(s, 0.6, 1.5, 5.6, 4.5, C.text1, "bio");
  s.addText([
    { text: "La bio proposée", options: { bold: true, fontSize: 14, color: C.accent5, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "🌺 Happiness providers since 1952", options: { breakLine: true } },
    { text: "🏖️ Plage, restaurant & Claudy's Bar", options: { breakLine: true } },
    { text: "📍 Pampelonne, Ramatuelle", options: { breakLine: true } },
    { text: "📲 Réserve ton bed en 1 clic 👇", options: {} },
  ], { x: 0.95, y: 1.8, w: 5.0, h: 3.0, fontSize: 21, color: C.background1, margin: 0, isTextBox: true, valign: "top" });
  s.addText("Un emoji en tête de chaque ligne : on lit la bio comme une petite carte.", { x: 0.95, y: 4.95, w: 5.0, h: 0.8, fontSize: 13, italic: true, color: C.background2, margin: 0, isTextBox: true });
  const etapes = [
    [fa.FaWhatsapp, C.accent2, "Un lien de réservation direct", "WhatsApp Business ou module de réservation : le client écrit ou réserve sans passer par une page intermédiaire."],
    [fa.FaLink, C.accent4, "Des liens clairs", "« Réserver un bed », « Réserver une table », « La carte » : chaque lien dit ce qu'il fait."],
    [fa.FaStar, C.accent3, "Des stories à la une utiles", "Réserver, Carte, Plage, Bar, Boutiques, Bien-être, Histoire : les réponses aux questions qu'on vous pose chaque jour."],
  ];
  for (let i = 0; i < etapes.length; i++) {
    const [ic, col, t, d] = etapes[i];
    const y = 1.5 + i * 1.5;
    await rondIcone(s, 6.7, y + 0.1, 0.8, col, ic, "etape" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
      { x: 7.7, y, w: 5.0, h: 1.3, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addNotes("Bio à valider avec l'équipe Moorea. Le choix entre WhatsApp Business et un module de réservation en ligne dépend de l'organisation de l'accueil.");

  // ---------- 12. Divider contenus ----------
  pres.addSection({ title: "Contenus" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Contenus" });
  s.background = { color: C.text2 };
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "div-contenus");
  s.addText("Les contenus", { placeholder: "title" });
  s.addText("Des formats pensés pour chaque réseau, au rythme des saisons", { placeholder: "body" });

  // ---------- 13. Formats ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Un format pour chaque envie", { placeholder: "title" });
  const formats = [
    [fa.FaFilm, C.accent3, "Réels et TikTok", ["« Une journée à Moorea », du ratissage au sunset", "Le geste des chefs en 15 secondes", "Les coulisses de l'ouverture", "Le coucher du soleil au Claudy's Bar"]],
    [fa.FaImages, C.accent4, "Carrousels", ["1952 → 2027 : l'album de famille", "La carte de la saison, plat par plat", "Le guide de Pampelonne par Moorea", "Les boutiques et le bien-être"]],
    [fa.FaMobileScreen, C.accent5, "Stories", ["Les beds disponibles du jour", "La suggestion du chef", "Sondages, quiz et questions", "Les coulisses en direct"]],
  ];
  for (let i = 0; i < formats.length; i++) {
    const [ic, col, t, items] = formats[i];
    const x = 0.6 + i * 4.1;
    carte(s, x, 1.5, 3.9, 5.1, C.background2, "format" + i);
    await rondIcone(s, x + 0.3, 1.8, 0.9, col, ic, "format" + i);
    s.addText(t, { x: x + 1.4, y: 1.8, w: 2.3, h: 0.9, fontSize: 19, bold: true, fontFace: "Bookman Old Style", color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText(items.map((it, k) => ({ text: it, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 3.0, w: 3.35, h: 3.3, fontSize: 17, color: C.text1, paraSpaceAfter: 14, margin: 0, isTextBox: true, valign: "top" });
  }

  // ---------- 14. Exemples ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Trois idées prêtes à tourner", { placeholder: "title" });
  const ex = [
    ["Réel", "Happiness providers", "Chaque membre de l'équipe dit en une phrase ce qui le rend heureux à Moorea. Sous-titres FR et EN.", C.accent3],
    ["Carrousel", "1952 → 2027", "Une photo d'archive, puis la même vue aujourd'hui. Dernière image : « Réserve ton bed pour la saison ».", C.accent5],
    ["Story", "La météo du bonheur", "Chaque matin : la mer, le soleil, les beds encore libres et un bouton pour réserver.", C.accent4],
  ];
  const exImg = ["ex-reel", "ex-carrousel", "ex-story"];
  ex.forEach(([type, t, d, col], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.57, y: 1.37, w: 2.76, h: 3.76, rectRadius: 0.22, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "cadre-" + i });
    s.addImage({ path: "photos/" + exImg[i] + ".jpg", x: x + 0.65, y: 1.45, w: 2.6, h: 3.6, altText: "Exemple " + type, objectName: "maquette-" + i });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.85, y: 1.65, w: 2.2, h: 0.4, rectRadius: 0.2, fill: { color: col }, line: { color: col }, objectName: "etiquette-" + i });
    s.addText(type.toUpperCase(), { x: x + 0.85, y: 1.65, w: 2.2, h: 0.4, fontSize: 12, bold: true, charSpacing: 3, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.8, y: 3.95, w: 2.3, h: 0.9, rectRadius: 0.1, fill: { color: C.background1, transparency: 10 }, line: { color: C.background1 }, objectName: "titre-maquette-" + i });
    s.addText(t, { x: x + 0.8, y: 3.95, w: 2.3, h: 0.9, fontSize: 18, italic: true, fontFace: "Bookman Old Style", color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(d, { x, y: 5.3, w: 3.9, h: 1.3, fontSize: 14, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addNotes("Photos des maquettes : mooreaplage.fr (cuisine, archives, ponton). Elles illustrent l'idée ; les vrais contenus seront tournés sur place.");

  // ---------- 15. L'année ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Contenus" });
  s.addText("Une année au rythme de la plage", { placeholder: "title" });
  const annee = [
    ["Novembre → mars", "L'hiver", "2 à 3 publications par semaine : archives, coulisses, temps forts annoncés en bio, comme le 18.12.", C.accent4],
    ["Mars → avril", "La réouverture", "Compte à rebours, installation des beds en vidéo, nouvelle carte : on fait revenir les habitués.", C.accent2],
    ["Mai → juin", "Le printemps", "Premiers bains, déjeuners au soleil, sunsets : on remplit les week-ends et les ponts.", C.accent5],
    ["Juillet → août", "La pleine saison", "Rythme quotidien, stories en direct, contenus en anglais : on gère la demande.", C.accent1],
    ["Septembre → octobre", "L'arrière-saison", "La plage plus calme, la lumière dorée, puis le « merci » de fin de saison.", C.accent3],
  ];
  s.addShape(pres.shapes.LINE, { x: 0.9, y: 2.75, w: 11.5, h: 0, line: { color: C.text2, width: 2 }, objectName: "frise" });
  annee.forEach(([p, t, d, col], i) => {
    const x = 0.6 + i * 2.47;
    s.addShape(pres.shapes.OVAL, { x: x + 0.85, y: 2.45, w: 0.6, h: 0.6, fill: { color: col }, line: { color: col }, objectName: "etape-annee-" + i });
    s.addText(p, { x, y: 1.85, w: 2.3, h: 0.4, fontSize: 14, bold: true, color: C.text2, align: "center", margin: 0, isTextBox: true });
    s.addText(t, { x, y: 3.3, w: 2.3, h: 0.5, fontSize: 19, bold: true, fontFace: "Bookman Old Style", color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.05, y: 3.95, w: 2.2, h: 2.1, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addText("Les dates d'ouverture, de fermeture et les temps forts de Saint-Tropez seront calés avec vous dans le calendrier éditorial de chaque mois.",
    { x: 0.6, y: 6.15, w: 12.1, h: 0.6, fontSize: 13, italic: true, color: C.text2, margin: 0, isTextBox: true });
  s.addNotes("Site mooreaplage.fr : « Réouverture le 12 avril » (année non précisée). Saison 2026 annoncée du 28 mars au 4 octobre par certaines fiches touristiques : dates à confirmer avec Moorea.");

  // ---------- 16. Divider offre ----------
  pres.addSection({ title: "Offre" });
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Offre" });
  s.background = { color: C.text1 };
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "div-offre");
  s.addText("Mon accompagnement", { placeholder: "title" });
  s.addText("Une formule pensée pour une plage : intense l'été, présente l'hiver", { placeholder: "body" });

  // ---------- 17. Offre ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("Deux rythmes, un seul fil", { placeholder: "title" });
  const offres = [
    ["Saison", "avril → octobre", "1 490 €", "par mois · formule Prestige", C.accent5, [
      "Instagram, TikTok et Facebook",
      "16 publications et 20 stories par mois",
      "6 réels et TikTok par mois, montés",
      "Une demi-journée photo et vidéo sur place à chaque saison",
      "Une campagne publicitaire Meta par mois (budget à part)",
      "Réponses aux messages et commentaires 6 j/7",
      "Rapport et point mensuel d'une heure",
    ]],
    ["Hiver", "novembre → mars", "490 €", "par mois · formule Essentielle", C.accent4, [
      "Instagram et Facebook",
      "8 publications et 8 stories par mois",
      "2 réels par mois, montés à partir des archives et des coulisses",
      "Calendrier éditorial validé avec vous",
      "Préparation de la saison suivante",
    ]],
  ];
  offres.forEach(([nom, per, prix, sous, col, items], i) => {
    const x = 0.6 + i * 6.15;
    carte(s, x, 1.45, 5.95, 5.3, C.background2, "offre" + i);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.3, y: 1.7, w: 5.35, h: 1.45, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: "entete-offre" + i });
    s.addText([{ text: nom, options: { fontFace: "Bookman Old Style", bold: true, fontSize: 22, breakLine: true } }, { text: per, options: { fontSize: 14 } }],
      { x: x + 0.55, y: 1.8, w: 2.6, h: 1.25, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    s.addText([{ text: prix, options: { fontFace: "Bookman Old Style", bold: true, fontSize: 30, breakLine: true } }, { text: sous, options: { fontSize: 12 } }],
      { x: x + 3.05, y: 1.8, w: 2.45, h: 1.25, color: C.text1, align: "right", margin: 0, isTextBox: true, valign: "middle" });
    s.addText(items.map((it, k) => ({ text: it, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.45, y: 3.35, w: 5.1, h: 3.25, fontSize: 14, color: C.text1, paraSpaceAfter: 6, margin: 0, isTextBox: true, valign: "top" });
  });
  s.addNotes("Tarifs repris de la grille de Margaux Krikorian (valable jusqu'au 30/06/2027). TVA non applicable, article 293 B du CGI. Budget publicitaire réglé directement par l'établissement à Meta (conseillé : 150 à 300 € par mois).");

  // ---------- 18. Récap annuel + options ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("L'année complète, en clair", { placeholder: "title" });
  carte(s, 0.6, 1.5, 5.4, 4.6, C.text1, "total");
  s.addText([
    { text: "7 mois de saison × 1 490 €", options: { breakLine: true } },
    { text: "5 mois d'hiver × 490 €", options: { breakLine: true } },
    { text: " ", options: { fontSize: 10, breakLine: true } },
    { text: "12 880 €", options: { fontFace: "Bookman Old Style", bold: true, fontSize: 48, color: C.accent5, breakLine: true } },
    { text: "pour l'année, TVA non applicable", options: { fontSize: 14 } },
  ], { x: 1.0, y: 1.85, w: 4.7, h: 3.2, fontSize: 18, color: C.background1, margin: 0, isTextBox: true, valign: "top" });
  s.addText("Mise en place offerte (audit, charte, profils) pour un engagement de 6 mois", { x: 1.0, y: 5.1, w: 4.7, h: 0.8, fontSize: 14, italic: true, color: C.background2, margin: 0, isTextBox: true });
  const opts = [
    [fa.FaCamera, C.accent1, "Séance photo supplémentaire", "600 € la demi-journée"],
    [fa.FaFilm, C.accent3, "Réel supplémentaire", "90 € le réel"],
    [fa.FaChampagneGlasses, C.accent5, "Couverture d'un événement", "Soirée, lancement, sunset : sur devis"],
    [fa.FaHandshake, C.accent2, "Conditions", "Engagement de 3 mois, puis sans engagement. Facturation mensuelle, paiement à 15 jours. Chaque contenu est validé par vous."],
  ];
  for (let i = 0; i < opts.length; i++) {
    const [ic, col, t, d] = opts[i];
    const y = 1.5 + i * 1.18;
    await rondIcone(s, 6.5, y + 0.1, 0.75, col, ic, "option" + i);
    s.addText([{ text: t, options: { bold: true, fontSize: 16, breakLine: true } }, { text: d, options: { fontSize: 13 } }],
      { x: 7.45, y, w: 5.25, h: 1.05, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
  }
  s.addNotes("Calcul : 7 × 1 490 = 10 430 € ; 5 × 490 = 2 450 € ; total 12 880 €. Le découpage des mois sera ajusté aux dates réelles d'ouverture.");

  // ---------- 19. Méthode ----------
  s = pres.addSlide({ masterName: "CONTENU", sectionTitle: "Offre" });
  s.addText("Comment nous travaillerons", { placeholder: "title" });
  const meth = [
    ["Semaine 1", "Rencontre sur place, accès aux comptes, audit des statistiques"],
    ["Semaine 2", "Charte réseaux, nouvelle bio, stories à la une, lien de réservation"],
    ["Semaine 3", "Premier calendrier éditorial et première séance photo et vidéo"],
    ["Chaque mois", "Calendrier validé par vous, publications, réponses, rapport et point d'une heure"],
  ];
  meth.forEach(([t, d], i) => {
    const x = 0.6 + i * 3.08;
    const col = [C.accent4, C.accent3, C.accent5, C.accent2][i];
    s.addShape(pres.shapes.OVAL, { x: x + 0.95, y: 1.6, w: 1.0, h: 1.0, fill: { color: col }, line: { color: col }, objectName: "methode-" + i });
    s.addText(String(i + 1), { x: x + 0.95, y: 1.6, w: 1.0, h: 1.0, fontSize: 28, bold: true, fontFace: "Bookman Old Style", color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.05, y: 2.1, w: 1.95, h: 0, line: { color: C.text2, width: 2, dashType: "dash" }, objectName: "fleche-" + i });
    s.addText(t, { x, y: 2.85, w: 2.9, h: 0.5, fontSize: 18, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.1, y: 3.4, w: 2.7, h: 1.8, fontSize: 16, color: C.text1, align: "center", margin: 0, isTextBox: true, valign: "top" });
  });
  carte(s, 0.6, 5.3, 12.1, 1.3, C.background2, "engagement");
  s.addText([{ text: "Mon engagement : ", options: { bold: true } }, { text: "rien n'est publié sans votre accord, les vidéos sont montées pour Instagram et pour TikTok, et vous gardez la main sur vos comptes à tout moment." }],
    { x: 0.9, y: 5.4, w: 11.5, h: 1.1, fontSize: 16, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });

  // ---------- 20. Fin ----------
  s = pres.addSlide({ masterName: "SOMBRE", sectionTitle: "Offre" });
  bulles(s, 0.8, 1.2, 0.55);
  photoDroite(s, "fin");
  s.addText("Faisons rayonner le bonheur de Moorea", { placeholder: "title" });
  s.addText([
    { text: "Prochaine étape : un rendez-vous sur place pour caler la saison 2027 ensemble.", options: { breakLine: true } },
    { text: "Margaux Krikorian · Community manager", options: { color: C.accent5, breakLine: true } },
    { text: "06\u00A016\u00A003\u00A080\u00A012", options: { color: C.accent5 } },
  ], { placeholder: "body" });
  s.addNotes("Sources de la présentation : mooreaplage.fr (pages histoire, plage, restaurant, bar, contact) ; so-edition.com/ambassadeurs/moorea ; lifemag.fr/moorea-plage ; blog.sttropezhouse.com (Club 55) ; frenchrivieraluxuryvillas.com (guide 2026) ; tourismembassy.com (clubs de plage 2026) ; wearejuno.fr ; magazine-acumen.com ; capture du profil Instagram @moorea_plage du 25/11/2026.");

  await pres.writeFile({ fileName: "Moorea-Plage-proposition.pptx" });
  await applyTheme("Moorea-Plage-proposition.pptx", THEME);
  console.log("ok");
})().catch(e => { console.error(e); process.exit(1); });
