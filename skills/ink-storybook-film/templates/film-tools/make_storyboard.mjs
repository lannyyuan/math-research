// 分镜 PPT：每条字幕一页（全屏 16:9 画面，字幕已在画面里），备注里写场景/时间码/字幕原文，按场景分节。
//   node scripts/storyboard_plan.mjs → 渲染取帧（stills.mjs --scale=1）→ 转 JPEG 放 out/ppt_jpg/NN.jpg → 本脚本
// 需要 pptxgenjs（npm i pptxgenjs，或用全局安装的）
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
const pptxgen = require('pptxgenjs');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const plan = JSON.parse(fs.readFileSync(path.join(root, 'out/storyboard_plan.json'), 'utf8'));

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333" × 7.5"
pres.title = '《雪地里的那盏灯》分镜画面';
pres.subject = '动画短片《雪地里的那盏灯》中所有带字幕的画面（41 张）';
pres.author = 'Claude';
pres.defineSlideMaster({title: '画面', background: {color: '0B1537'}});

let lastScene = null;
plan.forEach((p, i) => {
  if (p.scene !== lastScene) {
    pres.addSection({title: p.scene === 's0-title' ? '片头' : `${p.scene.replace(/^s(\d+)-.*/, '$1')} ${p.sceneName}`});
    lastScene = p.scene;
  }
  const slide = pres.addSlide({masterName: '画面', sectionTitle: p.scene === 's0-title' ? '片头' : `${p.scene.replace(/^s(\d+)-.*/, '$1')} ${p.sceneName}`});
  const line = p.text.replace(/\n/g, ' ');
  slide.addImage({
    path: path.join(root, `out/ppt_jpg/${String(i + 1).padStart(2, '0')}.jpg`),
    x: 0, y: 0, w: 13.333, h: 7.5,
    altText: `动画《雪地里的那盏灯》${p.sceneName}。字幕：${line}`,
    objectName: `画面 ${i + 1}`,
  });
  slide.addNotes(`${i + 1}/${plan.length}　场景：${p.sceneName}　时间码：${p.tc}\n字幕：${line}`);
});
const out = path.join(root, 'dist/snow-lamp-storyboard.pptx');
await pres.writeFile({fileName: out});
console.log('written', out, (fs.statSync(out).size / 1e6).toFixed(1) + ' MB', plan.length + ' slides');
