// Version MODIFIABLE des 20 stories « Piatti del giorno » : un PowerPoint (ouvrable dans Keynote ou PowerPoint sur iPad),
// une diapositive 9:16 par jour, la story en fond et une zone de texte à remplir avec les suggestions du jour.
// node outils/stories_modeles.js   (NODE_PATH vers pptxgenjs)
const pptxgen = require("pptxgenjs");
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "..");
const dir = path.join(R, "stories/da-laura/piatti-modeles/2026-12");
const prog = JSON.parse(fs.readFileSync(path.join(dir, "programme.json"), "utf8"));
const p = new pptxgen();
p.defineLayout({ name: "STORY", width: 5.625, height: 10 });
p.layout = "STORY";
const k = 5.625 / 1080;
for (const [date] of prog) {
  const s = p.addSlide();
  s.background = { path: path.join(dir, "fonds-pptx", `${date}.jpg`) };
  s.addText(
    [
      { text: "Suggestion 1", options: { bold: true, breakLine: true } },
      { text: "description · prix", options: { italic: true, fontSize: 13, breakLine: true } },
      { text: " ", options: { fontSize: 8, breakLine: true } },
      { text: "Suggestion 2", options: { bold: true, breakLine: true } },
      { text: "description · prix", options: { italic: true, fontSize: 13, breakLine: true } },
      { text: " ", options: { fontSize: 8, breakLine: true } },
      { text: "Suggestion 3", options: { bold: true, breakLine: true } },
      { text: "description · prix", options: { italic: true, fontSize: 13 } },
    ],
    { x: 140 * k, y: 1180 * k, w: 800 * k, h: 450 * k, fontFace: "Arial", fontSize: 18, color: "8E1D1D",
      align: "center", valign: "middle" }
  );
}
p.writeFile({ fileName: path.join(dir, "Piatti-del-giorno-decembre-2026-modifiable.pptx") }).then(f => console.log(f));
