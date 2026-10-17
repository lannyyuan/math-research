// 汽油车 vs 电动车 — 小学科学 PPT (pptxgenjs, structured deck)
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");

const W = path.resolve(__dirname, "..");
const P = (f) => path.join(W, f);
const b64 = (f) => "data:image/" + (f.endsWith(".png") ? "png" : "jpeg") + ";base64," + fs.readFileSync(P(f)).toString("base64");

const THEME = {
  name: "Kids Car Science",
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  colors: {
    dk1: "4A3B30", lt1: "FFFFFF", dk2: "A0582E", lt2: "FAF4E0",
    accent1: "E8771A", accent2: "2FA35F", accent3: "F1E8DF", accent4: "3D7BD9",
    accent5: "C9C4BA", accent6: "FDFBF4", hlink: "3D7BD9", folHlink: "6E5A9E",
  },
};
const HEX = { brown: "A0582E", ink: "4A3B30", cream: "FAF4E0", card: "FDFBF4", border: "C9C4BA", bubble: "F1E8DF", orange: "E8771A", green: "2FA35F", lav: "F4F4FF", lavCard: "FBFBFF", lavBorder: "C9CBE6", white: "FFFFFF" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 — same canvas as the two source decks
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "汽油车 vs 电动车：肚子里有什么？";
const C = pres.SchemeColor;

// ---- layouts (the source decks' frame: cream page + rounded card + brown title)
// The rounded card is baked into the background image (layouts can't hold a rounded shape);
// the title placeholder is built fresh per layout because pptxgenjs mutates it in place.
const titlePh = () => ({ placeholder: { options: { name: "title", type: "title", x: 0.94, y: 0.6, w: 11.4, h: 0.85, fontSize: 32, bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } });
pres.defineSlideMaster({ title: "CARD", background: { path: P("img/bg-card.png") }, objects: [titlePh()] });
pres.defineSlideMaster({ title: "CARD_EV", background: { path: P("img/bg-card-ev.png") }, objects: [titlePh()] });
pres.defineSlideMaster({ title: "PAGE", background: { color: HEX.cream }, objects: [] });

const addBubble = (s, x, y, w, h, runs, name) =>
  s.addText(runs, { x, y, w, h, shape: pres.ShapeType.roundRect, rectRadius: 0.22, fill: { color: HEX.bubble }, line: { color: HEX.bubble }, fontSize: 18, color: C.text1, valign: "middle", margin: [12, 16, 12, 16], isTextBox: true, objectName: name });
const chip = (s, x, y, w, h, text, color, name, size = 18) =>
  s.addText(text, { x, y, w, h, shape: pres.ShapeType.roundRect, rectRadius: 0.2, fill: { color }, line: { color }, fontSize: size, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: name });

// ---------------------------------------------------------------- 1 cover
pres.addSection({ title: "开场" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "开场" });
  s.addText("汽油车 vs 电动车", { placeholder: "title" });
  s.addText("肚子里有什么？一起拆开比一比！", { x: 0.94, y: 1.45, w: 11.4, h: 0.6, fontSize: 24, color: C.text1, margin: 0, isTextBox: true, objectName: "subtitle" });
  s.addImage({ data: b64("img/cover-gas.png"), x: 0.94, y: 2.35, w: 5.2, h: 2.55, rounding: true, objectName: "gasCar" });
  s.addImage({ data: b64("img/cover-ev.png"), x: 7.19, y: 2.35, w: 5.2, h: 2.55, rounding: true, objectName: "evCar" });
  s.addText("VS", { x: 6.17, y: 3.13, w: 1.0, h: 1.0, shape: pres.ShapeType.ellipse, fill: { color: HEX.brown }, line: { color: HEX.white, width: 3 }, fontSize: 26, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "vs" });
  chip(s, 2.29, 5.1, 2.5, 0.6, "汽油车", HEX.orange, "gasChip", 22);
  chip(s, 8.54, 5.1, 2.5, 0.6, "电动车", HEX.green, "evChip", 22);
  s.addText("小学科学 · 汽车大揭秘", { x: 0.94, y: 6.2, w: 11.4, h: 0.45, fontSize: 16, color: HEX.brown, align: "center", margin: 0, isTextBox: true, objectName: "tag" });
  s.addNotes("今天我们当一回“汽车小侦探”：把汽油车和电动车的肚子打开看看，比一比谁的结构更简单。先请同学们猜一猜：哪一辆车里面的零件更多？");
}

// ---------------------------------------------------------------- video slide helper
const videoSlide = ({ master, section, title, video, poster, accent, prompts, notes }) => {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addMedia({ type: "video", path: P(video), cover: b64(poster), x: 0.94, y: 1.65, w: 8.4, h: 4.725, objectName: "video" });
  s.addText("完整动画", { x: 9.65, y: 1.65, w: 2.7, h: 0.55, shape: pres.ShapeType.roundRect, rectRadius: 0.2, fill: { color: accent }, line: { color: accent }, fontSize: 18, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "tag" });
  addBubble(
    s, 9.65, 2.4, 2.75, 3.975,
    [
      { text: "后面每一页还有对应的小片段，可以先跳过。", options: { fontSize: 14, breakLine: true, paraSpaceAfter: 10 } },
      { text: "边看边找一找：", options: { bold: true, breakLine: true, paraSpaceAfter: 8 } },
      ...prompts.map((p, i) => ({ text: p, options: { bullet: { type: "number" }, breakLine: i < prompts.length - 1, paraSpaceAfter: 6 } })),
    ],
    "prompts",
  );
  s.addNotes(notes);
};
// Per-part clips cut from the narrated videos (clips/clips.tsv: name, source, start, end, poster time).
// Each clip sits in the largest empty 16:9 area of its page (free.py → place.py → free.json, page pixels at 192 px/in)
// and plays full screen on click (timing added by fullscreen.py after writeFile).
const CLIPS = Object.fromEntries(
  fs.readFileSync(P("clips/clips.tsv"), "utf8").trim().split("\n").map((l) => {
    const [name, src, a, b] = l.split("\t");
    return [name, { src, a: +a, b: +b }];
  }),
);
const FREE = JSON.parse(fs.readFileSync(P("free.json"), "utf8"));
const NARRATION = { gas: "汽油车", ev: "电动车" };
const fmt = (t) => `${Math.floor(t / 60)}:${(t % 60).toFixed(1).padStart(4, "0")}`;
const pageSlide = (name, section, extraNote = "") => {
  const s = pres.addSlide({ masterName: "PAGE", sectionTitle: section });
  s.addImage({ path: P(`img/${name}.png`), x: 0, y: 0, w: 13.333, h: 7.5, objectName: "page" });
  let notes = fs.readFileSync(P(`img/${name}.txt`), "utf8").trim();
  const clip = CLIPS[name];
  if (clip) {
    const [x, y, w, h] = FREE[name].place.map((v) => v / 192); // centred in the empty area (place.py)
    s.addMedia({ type: "video", path: P(`clips/${name}.mp4`), cover: b64(`clips/${name}-poster.jpg`), x, y, w, h, objectName: "clip" });
    notes += `\n\n点右上角的小视频，会全屏播放${NARRATION[clip.src]}动画的这一段（${fmt(clip.a)}–${fmt(clip.b)}，约 ${Math.round(clip.b - clip.a)} 秒，带旁白），播完回到这一页。`;
  }
  if (extraNote) notes += "\n\n" + extraNote;
  s.addNotes(notes);
};

// ---------------------------------------------------------------- gasoline car
pres.addSection({ title: "汽油车" });
videoSlide({
  master: "CARD", section: "汽油车", title: "第一站：汽油车的肚子里有什么？", video: "gas-car.mp4", poster: "poster-gas.jpg", accent: HEX.orange,
  prompts: ["油箱藏在哪里？", "活塞怎样上下跑？", "尾气从哪儿出来？"],
  notes: "播放动画（70 秒，自带旁白和字幕）。看完问：汽油从油箱出发，经过哪些地方，最后怎样让车轮转起来？动画最后，全车零件散开成“零件云”——会动的零件大约 2000 多个。\n\n两种上法：① 先放完整动画，再逐页讲；② 跳过这一页，在后面每个零件页点小视频，只放那一段。“零件云”结尾只在完整动画里。",
});
for (let i = 1; i <= 7; i++)
  pageSlide(`car${i}`, "汽油车", i === 4 ? "动画里的车是前轮驱动：发动机在前面，动力经变速箱、再由两根“半轴”送到前轮——半轴就是短短的传动轴。" : "");

// ---------------------------------------------------------------- electric car
pres.addSection({ title: "电动车" });
videoSlide({
  master: "CARD_EV", section: "电动车", title: "第二站：电动车的肚子里有什么？", video: "electric-car.mp4", poster: "poster-ev.jpg", accent: HEX.green,
  prompts: ["电池包铺在哪里？", "电流往哪儿跑？", "有没有排气管？"],
  notes: "播放动画（72 秒）。看完问：电动车的“三大件”是什么？（电池、电机、电控）电流总是从电池流到控制器，再流到电机。和汽油车比，车尾没有排气管，也不用换机油。\n\n两种上法：① 先放完整动画，再逐页讲；② 跳过这一页，在后面电池包、电机、电控页点小视频。单速减速器（0:40–0:50）、“车尾干干净净”（0:50–1:00）和拆车结尾只在完整动画里。",
});
for (const i of [1, 2, 3, 7])
  pageSlide(`ev${i}`, "电动车", i === 7 ? "动画里没有单独讲回收刹车，可以这样讲：踩刹车时，电机反过来变成“发电机”，车轮带着它转，发出的电又存回电池。" : "");

// ======================================================================
// The last three slides: compare, structure PK, China milestones.
// ======================================================================
const T = (s, text, o) => s.addText(text, { margin: 0, isTextBox: true, color: HEX.ink, ...o });
const panel = (s, x, y, w, h, fill, name) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.2, fill: { color: fill }, line: { color: fill }, objectName: name });
const arrow = (s, x, y, w, color, name) =>
  s.addShape(pres.ShapeType.rightArrow, { x, y, w, h: 0.3, fill: { color }, line: { color }, objectName: name });
const LIGHT = { orange: "FCE6D2", green: "DDF2E5", brownSoft: "D9B79F", grey: "D8D3CA" };

// ---------------------------------------------------------------- 15 比一比：零件数
pres.addSection({ title: "比一比" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("比一比：会动的零件有多少？", { placeholder: "title" });
  // left: the side-by-side teardown video
  s.addMedia({ type: "video", path: P("compare.mp4"), cover: b64("poster-compare.jpg"), x: 0.94, y: 1.6, w: 6.4, h: 3.6, objectName: "compareVideo" });
  T(s, "▶ 点一下，看两辆车同时拆开（11 秒）", { x: 0.94, y: 5.28, w: 6.4, h: 0.4, fontSize: 15, color: "7A6A5C", objectName: "videoHint" });

  // right: dot pictogram, one dot = 10 moving parts
  const px = 7.65, pw = 4.74;
  panel(s, px, 1.6, pw, 4.08, "FFFFFF", "dotsPanel");
  chip(s, px + 0.22, 1.78, 1.25, 0.42, "汽油车", HEX.orange, "gasChip", 16);
  T(s, [{ text: "≈ 2000", options: { bold: true, fontSize: 26, color: HEX.orange } }, { text: " 个", options: { fontSize: 16 } }], { x: px + 1.6, y: 1.72, w: 2.9, h: 0.52, valign: "middle", objectName: "gasCount" });
  const cols = 20, pitch = 0.215, d = 0.15, gx = px + (pw - cols * pitch) / 2 + (pitch - d) / 2, gy = 2.38;
  for (let i = 0; i < 200; i++)
    s.addShape(pres.ShapeType.ellipse, { x: gx + (i % cols) * pitch, y: gy + Math.floor(i / cols) * pitch, w: d, h: d, fill: { color: HEX.orange }, line: { color: HEX.orange, width: 0 }, objectName: `gasDot${i}` });
  const ey = gy + 10 * pitch + 0.2;
  chip(s, px + 0.22, ey, 1.25, 0.42, "电动车", HEX.green, "evChip", 16);
  T(s, [{ text: "≈ 20", options: { bold: true, fontSize: 26, color: HEX.green } }, { text: " 个", options: { fontSize: 16 } }], { x: px + 1.6, y: ey - 0.06, w: 1.6, h: 0.52, valign: "middle", objectName: "evCount" });
  for (let i = 0; i < 2; i++)
    s.addShape(pres.ShapeType.ellipse, { x: px + 3.0 + i * 0.3, y: ey + 0.12, w: 0.18, h: 0.18, fill: { color: HEX.green }, line: { color: HEX.green, width: 0 }, objectName: `evDot${i}` });
  T(s, "每个小圆点 = 10 个会动的零件", { x: px + 0.22, y: 5.22, w: pw - 0.44, h: 0.32, fontSize: 13, color: "7A6A5C", align: "right", objectName: "dotLegend" });

  addBubble(s, 0.94, 5.9, 11.45, 0.9, [
    { text: "零件越少，结构越简单：", options: { bold: true } },
    { text: "电动车会动的零件只有汽油车的大约 1/100，更不容易坏、更好修。" },
  ], "takeaway");
  s.addNotes("左边播放两辆车同时拆开的动画（11 秒，无声）。右边每个小圆点代表 10 个会动的零件：汽油车的发动机和变速箱里，会动的零件大约 2000 个（200 个圆点）；电动车的电机和减速器，大约 20 个（2 个圆点）。这两个数是常被引用的估算，只算“会转、会滑、会上下跑”的零件，不算螺丝和车身。");
}

// ---------------------------------------------------------------- 16 结构大 PK（简化版）
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("结构大 PK：谁的路更短？", { placeholder: "title" });
  const row = (y, label, color, light, parts, name) => {
    chip(s, 0.94, y, 1.3, 0.66, label, color, `${name}Label`, 20);
    const cw = 1.5, aw = 0.42, gap = 0.1;
    parts.forEach((p, i) => {
      const x = 2.5 + i * (cw + aw + 2 * gap);
      s.addText(p, { x, y, w: cw, h: 0.66, shape: pres.ShapeType.roundRect, rectRadius: 0.15, fill: { color: light }, line: { color, width: 1.5 }, fontSize: 20, bold: true, color: HEX.ink, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `${name}${i}` });
      if (i < parts.length - 1) arrow(s, x + cw + gap, y + 0.18, aw, color, `${name}Arrow${i}`);
    });
  };
  row(1.62, "汽油车", HEX.orange, LIGHT.orange, ["油箱", "发动机", "变速箱", "传动轴", "车轮"], "gas");
  T(s, "还要帮手：", { x: 2.5, y: 2.45, w: 1.4, h: 0.46, fontSize: 16, color: "7A6A5C", valign: "middle", objectName: "helpersLabel" });
  ["散热器", "机油", "排气管"].forEach((t, i) =>
    s.addText(t, { x: 3.85 + i * 1.3, y: 2.45, w: 1.15, h: 0.46, shape: pres.ShapeType.roundRect, rectRadius: 0.12, fill: { color: "FFFFFF" }, line: { color: HEX.orange, width: 1, dashType: "dash" }, fontSize: 16, color: HEX.ink, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `helper${i}` }),
  );
  row(3.2, "电动车", HEX.green, LIGHT.green, ["电池包", "电控", "电机", "减速器", "车轮"], "ev");

  // energy blocks: 10 shares of energy, how many push the wheels
  T(s, "10 份力气，有几份用来推车轮？", { x: 0.94, y: 4.35, w: 7.4, h: 0.46, fontSize: 20, bold: true, color: HEX.brown, valign: "middle", objectName: "blocksTitle" });
  const blocks = (y, label, color, light, solid, maybe, text, name) => {
    chip(s, 0.94, y, 1.3, 0.56, label, color, `${name}BlocksLabel`, 18);
    for (let i = 0; i < 10; i++) {
      const fill = i < solid ? color : i < solid + maybe ? light : "EFEAE2";
      s.addShape(pres.ShapeType.roundRect, { x: 2.5 + i * 0.5, y: y + 0.04, w: 0.42, h: 0.48, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: `${name}Block${i}` });
    }
    T(s, text, { x: 7.55, y, w: 1.25, h: 0.56, fontSize: 20, bold: true, valign: "middle", objectName: `${name}BlocksValue` });
  };
  blocks(4.98, "汽油车", HEX.orange, "F6C9A0", 2, 1, "2～3 份", "gas");
  blocks(5.72, "电动车", HEX.green, null, 8, 0, "8 份", "ev");

  s.addText([
    { text: "电动车：", options: { bold: true, breakLine: true, color: HEX.green } },
    { text: "路更短，", options: { breakLine: true } },
    { text: "力气浪费更少！" },
  ], { x: 8.9, y: 4.45, w: 3.49, h: 1.95, shape: pres.ShapeType.roundRect, rectRadius: 0.22, fill: { color: HEX.bubble }, line: { color: HEX.bubble }, fontSize: 26, bold: true, color: C.text1, align: "center", valign: "middle", margin: 8, isTextBox: true, objectName: "summary" });
  s.addNotes("上面两行是“动力走的路”：汽油车要经过油箱、发动机、变速箱、传动轴才到车轮，发动机还离不开散热器、机油和排气管这些帮手；电动车是电池包、电控、电机、减速器，再到车轮。\n\n下面的方块：把能量分成 10 份，汽油车只有 2～3 份真正推动车轮，其余大多变成热跑掉了；电动车有差不多 8 份。（美国能源部 fueleconomy.gov：汽油车约 12%–30%，电动车超过 77%。）\n\n可以补充：电动车刹车时，电机还能反过来发电，把力气存回电池（回收刹车）。");
}

// ---------------------------------------------------------------- 17 中国汽车（简化版）
pres.addSection({ title: "中国汽车" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "中国汽车" });
  s.addText("中国汽车：两个“世界第一”", { placeholder: "title" });
  const py = 1.55, ph = 4.9, ws = [3.3, 3.3, 4.35], xs = [0.94, 4.49, 8.04];
  const head = (i, year, title, color) => {
    panel(s, xs[i], py, ws[i], ph, "FFFFFF", `panel${i}`);
    T(s, year, { x: xs[i] + 0.22, y: py + 0.18, w: 1.5, h: 0.6, fontSize: 32, bold: true, color, valign: "middle", objectName: `year${i}` });
    T(s, title, { x: xs[i] + 0.22, y: py + 0.78, w: ws[i] - 0.44, h: 0.45, fontSize: 20, bold: true, color, valign: "middle", objectName: `head${i}` });
  };
  const caption = (i, text) => T(s, text, { x: xs[i] + 0.22, y: py + ph - 0.85, w: ws[i] - 0.44, h: 0.7, fontSize: 17, valign: "middle", objectName: `caption${i}` });
  const barOpts = (i, max, colors) => ({
    x: xs[i] + 0.1, y: py + 1.35, w: ws[i] - 0.2, h: 2.55, barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 50,
    chartColors: colors, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"万"', valAxisMaxVal: max, valAxisMinVal: 0,
    catAxisLabelColor: HEX.ink, catAxisLabelFontSize: 17, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showValue: true, dataLabelFontSize: 15, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.ink, dataLabelFontBold: true, showLegend: false,
  });

  head(0, "2009", "造车最多", HEX.brown);
  s.addChart(pres.ChartType.bar, [{ name: "2009 年造车数量（万辆）", labels: ["中国", "日本", "美国"], values: [1379, 793, 571] }], { ...barOpts(0, 1900, [HEX.brown, "C9C4BA", "C9C4BA"]), objectName: "productionChart" });
  caption(0, "从这一年起，中国年年造车世界第一。");

  head(1, "2023", "卖到国外最多", HEX.brown);
  s.addChart(pres.ChartType.bar, [{ name: "2023 年出口（万辆）", labels: ["中国", "日本"], values: [491, 442] }], { ...barOpts(1, 680, [HEX.brown, "C9C4BA"]), barGapWidthPct: 90, objectName: "exportChart" });
  caption(1, "卖到国外的车，比日本还多。");

  head(2, "2025", "新能源车快到一半", HEX.green);
  const cw = 0.74, ch = cw * 340 / 600, gap = 0.1, gx = xs[2] + (ws[2] - (5 * cw + 4 * gap)) / 2;
  for (let i = 0; i < 10; i++)
    s.addImage({ path: P(`img/icon-${i < 5 ? "ev" : "grey"}.png`), x: gx + (i % 5) * (cw + gap), y: py + 1.55 + Math.floor(i / 5) * (ch + 0.3), w: cw, h: ch, objectName: `car${i}` });
  const ly = py + 1.55 + 2 * (ch + 0.3) + 0.05;
  s.addImage({ path: P("img/icon-ev.png"), x: gx, y: ly + 0.06, w: 0.42, h: 0.24, objectName: "legendEv" });
  T(s, "新能源车", { x: gx + 0.5, y: ly, w: 1.2, h: 0.36, fontSize: 14, color: "7A6A5C", valign: "middle", objectName: "legendEvText" });
  s.addImage({ path: P("img/icon-grey.png"), x: gx + 1.85, y: ly + 0.06, w: 0.42, h: 0.24, objectName: "legendGas" });
  T(s, "烧油的车", { x: gx + 2.35, y: ly, w: 1.2, h: 0.36, fontSize: 14, color: "7A6A5C", valign: "middle", objectName: "legendGasText" });
  caption(2, "10 辆新车，约 5 辆是新能源车。");

  T(s, "数据：中国汽车工业协会、OICA", { x: 0.94, y: 6.6, w: 11.45, h: 0.3, fontSize: 11, color: "7A6A5C", objectName: "sources" });
  s.addNotes("① 2009 年，中国一年造了 1379 万辆车，超过日本（793 万）和美国（571 万），成为世界第一，到 2025 年已经连续 17 年第一（2025 年 3453 万辆）。\n② 2023 年，中国卖到国外的车有 491 万辆，超过日本（442 万），成为出口世界第一；2025 年出口 710 万辆。\n③ 2025 年，全部新车里新能源车（纯电动 + 插电混动）占 47.9%，差不多一半；只算国内卖出的新车，已经超过一半（国内乘用车 54%）。2020 年这个比例只有 5.4%，五年里涨了快 10 倍。\n数据来源：中国汽车工业协会、OICA。");
}

(async () => {
  const out = P("汽油车vs电动车-小学科学.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
