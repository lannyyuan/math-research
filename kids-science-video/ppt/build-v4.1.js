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

const NV = process.env.VARIANT === "nv";
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 — same canvas as the two source decks
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "新能源车肚子里的秘密";
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
  s.addText("新能源车肚子里的秘密", { placeholder: "title" });
  s.addText("汽油车 vs 电动车，一起拆开比一比！", { x: 0.94, y: 1.45, w: 11.4, h: 0.6, fontSize: 24, color: C.text1, margin: 0, isTextBox: true, objectName: "subtitle" });
  s.addImage({ data: b64("img/cover-gas.png"), x: 0.94, y: 2.35, w: 5.2, h: 2.55, rounding: true, objectName: "gasCar" });
  s.addImage({ data: b64("img/cover-ev.png"), x: 7.19, y: 2.35, w: 5.2, h: 2.55, rounding: true, objectName: "evCar" });
  s.addText("VS", { x: 6.17, y: 3.13, w: 1.0, h: 1.0, shape: pres.ShapeType.ellipse, fill: { color: HEX.brown }, line: { color: HEX.white, width: 3 }, fontSize: 26, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "vs" });
  chip(s, 2.29, 5.1, 2.5, 0.6, "汽油车", HEX.orange, "gasChip", 22);
  chip(s, 8.54, 5.1, 2.5, 0.6, "电动车", HEX.green, "evChip", 22);
  s.addText("小学科学 · 汽车大揭秘", { x: 0.94, y: 6.2, w: 11.4, h: 0.45, fontSize: 16, color: HEX.brown, align: "center", margin: 0, isTextBox: true, objectName: "tag" });
  s.addNotes("今天我们当一回“汽车小侦探”：把汽油车和电动车的肚子打开看看，比一比谁的结构更简单。先请同学们猜一猜：哪一辆车里面的零件更多？");
}

// ---------------------------------------------------------------- video slide helper
// Section opener ("第一站 / 第二站"): a still of the car plus the questions the next pages answer.
// The full videos are gone in v4.1 — every part page carries its own clip.
const stationSlide = ({ master, section, title, poster, accent, prompts, notes }) => {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addImage({ path: P(poster), x: 0.94, y: 1.65, w: 8.4, h: 4.725, rounding: false, objectName: "carStill" });
  s.addText("先找一找", { x: 9.65, y: 1.65, w: 2.7, h: 0.55, shape: pres.ShapeType.roundRect, rectRadius: 0.2, fill: { color: accent }, line: { color: accent }, fontSize: 18, bold: true, color: HEX.white, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "tag" });
  addBubble(
    s, 9.65, 2.4, 2.75, 3.975,
    [
      { text: "跟我一起找答案：", options: { bold: true, breakLine: true, paraSpaceAfter: 8 } },
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
// Part pages, rebuilt from the original page art (split.py → img/split/): the watercolour and the
// title are the original pixels; the speech bubble is re-set as live text in the original colours.
// Layout: illustration as tall as the content area on its original side; the other column holds
// the clip (top, plays full screen on click) and the bubble (bottom), edges aligned to the art.
const SPLIT = JSON.parse(fs.readFileSync(P("split.json"), "utf8"));
// Primary-school wording ("这个是…" + one working principle each). Lines are broken at phrase
// boundaries (≤12 characters for the narrow column, ≤17 for the wide one) so no phrase is split.
const BUBBLE_TEXT = {
  car1: "这个是油箱，\n一般装在后排座椅下面。\n它储存汽油，\n油泵再把汽油\n沿着油管送进发动机。",
  car2: "这个是发动机。\n火花塞点燃汽油和空气，\n燃烧产生的力量\n推动活塞上下运动，\n带动曲轴转起来。",
  car3: "这个是变速箱。\n它用大小不同的齿轮配合：\n低挡力气大，适合起步；\n高挡转得快，适合快跑。",
  car4: "这个是传动轴。\n它把变速箱输出的转动\n传给车轮，车轮转起来，\n汽车就前进了。",
  car5: "这个是散热器。\n发动机工作时会变得很热，\n冷却液把热量带到这里，\n风一吹就变凉，\n再流回发动机。",
  car6: "这个是机油。\n它在零件之间\n形成一层薄薄的油膜，\n减少摩擦和磨损，\n还能帮发动机散热。",
  car7: "这个是排气管。\n它把燃烧后产生的废气\n排出车外，上面的消声器\n还能让声音变小。",
  ev1: "这个是电池包，\n由许多块电池组成，\n平铺在车底。它储存电能，\n再把电送给电机。",
  ev2: "这个是电机。线圈通电后产生磁场，\n推动转子转动，\n把电能变成让车轮转动的动能。",
  ev3: "这个是电控，\n电动车的“大脑”。\n司机踩踏板，\n它就调节送给电机的电，\n控制车开得快还是慢。",
  ev7: "这个是回收刹车。\n减速刹车时，\n电机会变成发电机，\n把汽车的动能变回电能，\n存进电池里。",
};
const pageSlide = (name, section, extraNote = "") => {
  const gas = name.startsWith("car");
  const s = pres.addSlide({ masterName: gas ? "CARD" : "CARD_EV", sectionTitle: section });
  const o = SPLIT[name];
  // title: original lettering, original position and size
  const [tx0, ty0, tx1, ty1] = o.title;
  s.addImage({ path: P(`img/split/${name}-title.png`), x: (tx0 - 6) / 192, y: (ty0 - 6) / 192, w: (tx1 - tx0 + 13) / 192, h: (ty1 - ty0 + 13) / 192, altText: fs.readFileSync(P(`img/${name}.txt`), "utf8").trim(), objectName: "title" });
  const top = 1.55, bottom = 6.85, left = 0.94, right = 12.39, gap = 0.35, H = bottom - top;
  const [pw, ph] = o.illPx, iw = (H * pw) / ph;
  const colW = right - left - iw - gap;
  const ix = o.side === "L" ? left : right - iw, cx = o.side === "L" ? left + iw + gap : left;
  s.addImage({ path: P(`img/split/${name}-ill.png`), x: ix, y: top, w: iw, h: H, altText: BUBBLE_TEXT[name].replace(/\n/g, ""), objectName: "illustration" });
  const clip = CLIPS[name];
  let by = top;
  if (clip) {
    const vh = Math.min((colW * 9) / 16, H - 1.7 - gap), vw = (vh * 16) / 9;
    s.addMedia({ type: "video", path: P(`${NV ? "clips-nv" : "clips"}/${name}.mp4`), cover: b64(`clips/${name}-poster.jpg`), x: cx + (colW - vw) / 2, y: top, w: vw, h: vh, objectName: "clip" });
    by = top + vh + gap;
  }
  let bh = bottom - by;
  if (!clip) { bh = 3.0; by = top + (H - bh) / 2; }
  s.addText(BUBBLE_TEXT[name], {
    x: cx, y: by, w: colW, h: bh, shape: pres.ShapeType.roundRect, rectRadius: 0.2,
    fill: { color: gas ? "F2E7DB" : "F1EDEB" }, line: { color: gas ? "F2E7DB" : "F1EDEB" },
    fontSize: 22, color: gas ? "2A2420" : "1F2329", lineSpacingMultiple: 1.2, valign: "middle", margin: [14, 24, 14, 24], isTextBox: true, objectName: "bubble",
  });
  let notes = fs.readFileSync(P(`img/${name}.txt`), "utf8").trim();
  if (clip) notes += `\n\n点小视频，会全屏播放${NARRATION[clip.src]}动画的这一段（${fmt(clip.a)}–${fmt(clip.b)}，约 ${Math.round(clip.b - clip.a)} 秒，${NV ? "没有解说，由小讲解员现场讲" : "带旁白"}），播完回到这一页。`;
  if (extraNote) notes += "\n\n" + extraNote;
  s.addNotes(notes);
};

// ---------------------------------------------------------------- gasoline car
pres.addSection({ title: "汽油车" });
stationSlide({
  master: "CARD", section: "汽油车", title: "第一站：汽油车的肚子里有什么？", poster: "poster-gas.jpg", accent: HEX.orange,
  prompts: ["油箱藏在哪里？", "活塞怎样上下跑？", "尾气从哪儿出来？"],
  notes: "汽油车这一站的开始。先把三个问题抛给大家，接下来 7 页一页一页找答案：油箱在后排座椅下面；火花塞点燃汽油，推动活塞上下跑；尾气从车尾的排气管出来。每个零件页都有一段小动画，点一下就全屏播放。",
});
for (let i = 1; i <= 7; i++)
  pageSlide(`car${i}`, "汽油车", i === 4 ? "动画里的车是前轮驱动：发动机在前面，动力经变速箱、再由两根“半轴”送到前轮——半轴就是短短的传动轴。" : "");

// ---------------------------------------------------------------- electric car
pres.addSection({ title: "电动车" });
stationSlide({
  master: "CARD_EV", section: "电动车", title: "第二站：电动车的肚子里有什么？", poster: "poster-ev.jpg", accent: HEX.green,
  prompts: ["电池包铺在哪里？", "电流往哪儿跑？", "有没有排气管？"],
  notes: "电动车这一站的开始。先抛出三个问题，接下来 4 页找答案：电池包平铺在车底；电流从电池流到电控，再流到电机；电动车没有排气管，也不用换机油。",
});
for (const i of [1, 2, 3, 7])
  pageSlide(`ev${i}`, "电动车", i === 7 ? "动画里没有单独讲回收刹车，可以这样讲：踩刹车时，电机反过来变成“发电机”，车轮带着它转，发出的电又存回电池。" : "");

// ======================================================================
// Kids version (under 8) of the last three slides.
// ======================================================================
const T = (s, text, o) => s.addText(text, { margin: 0, isTextBox: true, color: HEX.ink, ...o });
const panel = (s, x, y, w, h, fill, name) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.2, fill: { color: fill }, line: { color: fill }, objectName: name });
const bigBubble = (s, x, y, w, h, text, name) =>
  s.addText(text, { x, y, w, h, shape: pres.ShapeType.roundRect, rectRadius: 0.22, fill: { color: HEX.bubble }, line: { color: HEX.bubble }, fontSize: 28, bold: true, color: HEX.ink, align: "center", valign: "middle", margin: 6, isTextBox: true, objectName: name });
const CAR = 340 / 600, TREE = 360 / 300;

// ---------------------------------------------------------------- 15 谁的零件多？
pres.addSection({ title: "比一比" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("比一比：谁的零件多？", { placeholder: "title" });
  s.addMedia({ type: "video", path: P("compare.mp4"), cover: b64("poster-compare.jpg"), x: 0.94, y: 1.6, w: 6.4, h: 3.6, objectName: "compareVideo" });
  T(s, "▶ 点一下，看两辆车拆开", { x: 0.94, y: 5.28, w: 6.4, h: 0.4, fontSize: 18, color: "7A6A5C", objectName: "videoHint" });

  const px = 7.65, pw = 4.74;
  panel(s, px, 1.6, pw, 4.08, "FFFFFF", "dotsPanel");
  chip(s, px + 0.22, 1.78, 1.3, 0.48, "汽油车", HEX.orange, "gasChip", 18);
  T(s, "零件好多好多！", { x: px + 1.68, y: 1.78, w: 2.9, h: 0.48, fontSize: 22, bold: true, color: HEX.orange, valign: "middle", objectName: "gasMany" });
  const cols = 20, pitch = 0.215, d = 0.15, gx = px + (pw - cols * pitch) / 2 + (pitch - d) / 2, gy = 2.42;
  for (let i = 0; i < 200; i++)
    s.addShape(pres.ShapeType.ellipse, { x: gx + (i % cols) * pitch, y: gy + Math.floor(i / cols) * pitch, w: d, h: d, fill: { color: HEX.orange }, line: { color: HEX.orange, width: 0 }, objectName: `gasDot${i}` });
  const ey = gy + 10 * pitch + 0.28;
  chip(s, px + 0.22, ey, 1.3, 0.48, "电动车", HEX.green, "evChip", 18);
  T(s, "零件少少的", { x: px + 1.68, y: ey, w: 1.9, h: 0.48, fontSize: 22, bold: true, color: HEX.green, valign: "middle", objectName: "evFew" });
  for (let i = 0; i < 2; i++)
    s.addShape(pres.ShapeType.ellipse, { x: px + 3.75 + i * 0.32, y: ey + 0.15, w: 0.2, h: 0.2, fill: { color: HEX.green }, line: { color: HEX.green, width: 0 }, objectName: `evDot${i}` });

  bigBubble(s, 0.94, 5.9, 11.45, 0.9, "零件少，就不容易坏！", "takeaway");
  s.addNotes("左边：点一下，两辆车同时拆开（11 秒）。右边：橙色小圆点是汽油车会动的零件，好多好多；绿色的是电动车，只有一点点。（老师参考：常见估算，汽油车会动的零件约 2000 个，电动车约 20 个；这里每个圆点约代表 10 个。）\n\n可以问小朋友：零件多的车和零件少的车，哪个更容易坏？");
}

// ---------------------------------------------------------------- 16 新能源车越来越多
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("在中国，新能源车越来越多！", { placeholder: "title" });
  T(s, [{ text: "每 10 辆新车里，" }, { text: "绿色的", options: { bold: true, color: HEX.green } }, { text: "是新能源车" }], { x: 0.94, y: 1.55, w: 11.4, h: 0.5, fontSize: 22, valign: "middle", objectName: "hint" });
  const rows = [["2021 年", 1], ["2023 年", 3], ["2025 年", 5]];
  const cw = 0.78, ch = cw * CAR, gap = 0.1, x0 = 2.6;
  rows.forEach(([year, n], r) => {
    const y = 2.3 + r * 1.05;
    chip(s, 0.94, y + (ch - 0.56) / 2, 1.4, 0.56, year, HEX.brown, `year${r}`, 20);
    for (let i = 0; i < 10; i++)
      s.addImage({ path: P(`img/icon-${i < n ? "ev" : "grey"}.png`), x: x0 + i * (cw + gap), y, w: cw, h: ch, objectName: `car${r}_${i}` });
    T(s, [{ text: String(n), options: { fontSize: 36, bold: true, color: HEX.green } }, { text: " 辆", options: { fontSize: 22, bold: true } }], { x: x0 + 10 * (cw + gap) + 0.15, y: y - 0.1, w: 1.2, h: ch + 0.2, valign: "middle", objectName: `count${r}` });
  });
  bigBubble(s, 0.94, 5.65, 11.45, 1.1, "绿色的车，越来越多啦！", "takeaway");
  s.addNotes("每一行是 10 辆新车，绿色的是新能源车（纯电动和插电混动）。2021 年，10 辆里大约只有 1 辆；2023 年大约 3 辆；2025 年差不多 5 辆，快到一半了。\n\n老师参考（中国汽车工业协会，新能源车占新车销量）：2021 年 13.4%，2023 年 31.6%，2025 年 47.9%；只算国内卖出的新车，2025 年已经超过一半。");
}

// ---------------------------------------------------------------- 17 卖到全世界，帮地球种树
pres.addSection({ title: "中国汽车" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "中国汽车" });
  s.addText("卖到全世界，帮地球种树！", { placeholder: "title" });
  // left: NEV exports keep growing
  panel(s, 0.94, 1.55, 5.4, 4.0, "FFFFFF", "exportPanel");
  T(s, "卖到外国的新能源车", { x: 1.16, y: 1.7, w: 5, h: 0.5, fontSize: 22, bold: true, color: HEX.green, valign: "middle", objectName: "exportTitle" });
  s.addChart(pres.ChartType.bar, [{ name: "新能源车出口（万辆）", labels: ["2021 年", "2023 年", "2025 年"], values: [31, 120, 262] }], {
    x: 1.04, y: 2.25, w: 5.2, h: 3.2, barDir: "col", barGapWidthPct: 70, chartColors: [HEX.green],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"万辆"', dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelColor: HEX.ink, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.ink, catAxisLabelFontSize: 18, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 310, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, objectName: "exportChart",
  });

  // right: one car ≈ 50 trees
  panel(s, 6.6, 1.55, 5.79, 4.0, "FFFFFF", "treePanel");
  s.addImage({ path: P("img/icon-ev.png"), x: 6.85, y: 1.72, w: 1.0, h: 1.0 * CAR, objectName: "oneCar" });
  T(s, [{ text: "1 辆新能源车 ≈ ", options: { fontSize: 22, bold: true } }, { text: "50 棵树", options: { fontSize: 26, bold: true, color: HEX.green } }], { x: 7.95, y: 1.68, w: 4.3, h: 0.66, valign: "middle", objectName: "equation" });
  const tw = 0.38, th = tw * TREE, tg = 0.1, tx = 6.6 + (5.79 - (10 * tw + 9 * tg)) / 2;
  for (let i = 0; i < 50; i++)
    s.addImage({ path: P("img/icon-tree.png"), x: tx + (i % 10) * (tw + tg), y: 2.5 + Math.floor(i / 10) * (th + 0.02), w: tw, h: th, objectName: `tree${i}` });
  T(s, "车开一年少排的气，要 50 棵大树才吸得完", { x: 6.85, y: 5.08, w: 5.3, h: 0.4, fontSize: 16, color: "7A6A5C", align: "center", valign: "middle", objectName: "treeNote" });

  bigBubble(s, 0.94, 5.75, 11.45, 1.05, "2025 年卖到外国的新能源车，一年就像种了 1 亿多棵树！", "takeaway");
  s.addNotes("左边：中国卖到外国的新能源车越来越多——2021 年 31 万辆，2023 年 120 万辆，2025 年 262 万辆（中国汽车工业协会）。\n\n右边：一辆新能源车开一年，比烧油的车少排的二氧化碳（让地球变热的气体），大约等于 50 棵大树一年吸收的量。2025 年出口的 262 万辆新能源车，一年就相当于种了 1 亿多棵树（262 万 × 50 ≈ 1.3 亿）。\n\n老师参考（估算，取保守值）：国际能源署（IEA）的全生命周期比较，一辆电动车每年比汽油车少排约 1.1–1.6 吨二氧化碳；一棵成年树一年大约吸收 22 千克二氧化碳（欧洲环境署常被引用的数字）。1.1 吨 ÷ 22 千克 ≈ 50 棵。实际多少和电是怎么发的、车开多远都有关系。");
}

(async () => {
  const out = P(NV ? "汽油车vs电动车-小学科学-v4.1-无解说.pptx" : "汽油车vs电动车-小学科学-v4.1.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
