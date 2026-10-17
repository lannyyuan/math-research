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

// ---------------------------------------------------------------- compare video
pres.addSection({ title: "比一比" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("比一比：把两辆车拆开看看", { placeholder: "title" });
  chip(s, 0.94, 1.65, 5.6, 0.62, "汽油车：零件云，会动的零件 ≈ 2000+", HEX.orange, "gasChip");
  chip(s, 6.79, 1.65, 5.6, 0.62, "电动车：几个大块，会动的零件 ≈ 20", HEX.green, "evChip");
  s.addMedia({ type: "video", path: P("compare.mp4"), cover: b64("poster-compare.jpg"), x: 0.94, y: 2.45, w: 11.45, h: 3.22, objectName: "compareVideo" });
  addBubble(s, 0.94, 5.85, 11.45, 0.95, [
    { text: "零件越少，结构越简单：", options: { bold: true } },
    { text: "更不容易坏、更好修，也更省力气。" },
  ], "takeaway");
  s.addNotes("同时播放两段“拆车”动画（11 秒，无声，老师讲解）：左边汽油车散开成一片零件云，右边电动车只散开几个大块。请同学们数一数右边有几块：电池包、高压线束、控制器、电机、减速器、半轴、车轮。");
}

// ---------------------------------------------------------------- structure table
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "比一比" });
  s.addText("结构大 PK：电动车简单在哪里？", { placeholder: "title" });
  const rows = [
    ["能量", "油箱装汽油", "电池包存电"],
    ["动力", "发动机：4 个活塞上下跑，好多零件一起配合", "电机：一通电就转，只有定子和转子"],
    ["换挡", "变速箱：要在好几个挡之间换来换去", "单速减速器：1 个挡就够用"],
    ["保养", "要换机油，还要散热器帮忙降温", "不用换机油"],
    ["尾气", "排气管冒出尾气", "没有排气管，不冒烟"],
    ["刹车", "刹车时，力气变成热，白白浪费", "回收刹车：把力气变回电，存进电池"],
  ];
  const head = (t, fill) => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: fill }, align: "center", fontSize: 18 } });
  const table = [[head("", HEX.brown), head("汽油车", HEX.orange), head("电动车", HEX.green)]].concat(
    rows.map((r) => [
      { text: r[0], options: { bold: true, color: HEX.brown, align: "center", fill: { color: HEX.bubble } } },
      { text: r[1], options: { fill: { color: "FFF4E8" } } },
      { text: r[2], options: { fill: { color: "EAF7EE" } } },
    ]),
  );
  s.addTable(table, { x: 0.94, y: 1.6, w: 11.45, colW: [1.35, 5.05, 5.05], rowH: 0.62, fontSize: 16, color: HEX.ink, valign: "middle", border: { type: "solid", pt: 1.5, color: HEX.card }, margin: [4, 10, 4, 10], objectName: "pkTable" });
  addBubble(s, 0.94, 6.08, 11.45, 0.72, [{ text: "电动车 = 简单的三大件（电池 · 电机 · 电控）    汽油车 = 复杂的小工厂", options: { bold: true } }], "summary");
  s.addNotes("小结：电动车把“发动机 + 多挡变速箱 + 机油 + 排气”这一大套换成了“电池 + 电机 + 电控”三大件。零件少，坏的地方就少；刹车时电机还能反过来发电，把能量存回电池。也可以提醒同学们：电动车需要充电，旧电池要好好回收利用。");
}

// ---------------------------------------------------------------- China milestones (last slide)
pres.addSection({ title: "中国汽车" });
{
  const s = pres.addSlide({ masterName: "CARD", sectionTitle: "中国汽车" });
  s.addText("中国汽车：两个“世界第一”，电动车“过半”", { placeholder: "title" });
  s.addShape(pres.ShapeType.line, { x: 2.27, y: 2.55, w: 8.79, h: 0, line: { color: HEX.border, width: 3 }, objectName: "timeline" });
  const items = [
    { year: "2009", color: HEX.brown, head: "汽车产量世界第一", body: "一年造了 1379 万辆车，超过美国和日本，之后一直保持第一" },
    { year: "2023", color: HEX.brown, head: "汽车出口世界第一", body: "一年卖到国外 491 万辆，超过日本（442 万辆）" },
    { year: "2024.7", color: HEX.green, head: "新能源车首次单月过半", body: "这个月卖出的新乘用车里，51.1% 是新能源车" },
    { year: "2025", color: HEX.green, head: "新能源车全年过半", body: "国内全年卖出的新车里，新能源车比燃油车多" },
  ];
  items.forEach((it, i) => {
    const cx = 2.27 + i * 2.93;
    s.addShape(pres.ShapeType.ellipse, { x: cx - 0.18, y: 2.37, w: 0.36, h: 0.36, fill: { color: it.color }, line: { color: HEX.white, width: 2 }, objectName: `dot${i}` });
    s.addText(it.year, { x: cx - 1.4, y: 1.62, w: 2.8, h: 0.65, fontSize: 36, bold: true, color: it.color, align: "center", margin: 0, isTextBox: true, objectName: `year${i}` });
    s.addText(
      [
        { text: it.head, options: { bold: true, fontSize: 16, color: it.color, breakLine: true, paraSpaceAfter: 8 } },
        { text: it.body, options: { fontSize: 17, color: HEX.ink } },
      ],
      { x: cx - 1.38, y: 3.0, w: 2.76, h: 2.45, shape: pres.ShapeType.roundRect, rectRadius: 0.2, fill: { color: it.color === HEX.green ? "EAF7EE" : HEX.bubble }, line: { color: it.color === HEX.green ? "EAF7EE" : HEX.bubble }, valign: "top", margin: [12, 12, 12, 12], isTextBox: true, objectName: `card${i}` },
    );
  });
  s.addText("注：新能源车包括纯电动车和插电混动车。2024 年 7 月为乘用车零售口径（乘联会）；2025 年为国内新车销量口径（中汽协，连出口一起算约 47.9%）；产量、出口数据来自中汽协。", {
    x: 0.94, y: 5.75, w: 11.45, h: 0.9, fontSize: 12, color: "7A6A5C", margin: 0, valign: "top", isTextBox: true, objectName: "sources",
  });
  s.addNotes("2009 年中国汽车产量 1379 万辆，第一次成为世界第一，以后年年第一。2023 年中国出口汽车 491 万辆，超过日本，成为出口第一（2024、2025 年继续第一，2025 年超过 700 万辆）。2024 年 7 月，新能源乘用车的零售量第一次超过一半（51.1%）；2025 年，国内全年新车销量里新能源车超过一半——新能源车第一次在一整年里卖得比燃油车多。数据来源：中国汽车工业协会、乘用车市场信息联席会。");
}

(async () => {
  const out = P("汽油车vs电动车-小学科学.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
