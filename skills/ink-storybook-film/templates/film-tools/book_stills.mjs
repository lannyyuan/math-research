// 绘本网页要用的全部插图（不带字幕的干净画面）：
//   1. 片头 + 40 条字幕各一张（取字幕停留 70% 处，和分镜 PPT 同一帧）→ out/book_img/cue/
//   2. 补充插图 10 张（src/plates/Plates.tsx）→ out/book_img/plate/
//   3. 影片里挑的几张过渡画面 → out/book_img/film/
// 用法： node scripts/storyboard_plan.mjs && node scripts/book_stills.mjs [--scale=1]
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {sceneStarts} from '../src/schedule.mjs';

const timeline = JSON.parse(fs.readFileSync('src/timeline.json', 'utf8'));
const starts = sceneStarts(timeline);
const plan = JSON.parse(fs.readFileSync('out/storyboard_plan.json', 'utf8'));
const scale = parseFloat((process.argv.find((a) => a.startsWith('--scale=')) ?? '--scale=1').split('=')[1]);
const only = (process.argv.find((a) => a.startsWith('--only=')) ?? '').split('=')[1];
const browserExecutable = process.env.REMOTION_BROWSER ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), onProgress: () => {}});

const PLATES = ['shadows', 'questions', 'farm', 'snowman', 'wall', 'school', 'sea', 'stars', 'deernight', 'contest'];
// 影片里挑的过渡画面：名字 → [场景序号(0 起), 场景内秒]
const FILM = {
  cover: [0, 0.75], // 封面：片头场景里题目还没浮现的那一刻
  'cave-home': [5, 11.2], // 山洞火堆边，圆窗里是家
  'spring-meadow': [7, 8.5], // 冰雪化了，绿草地
  'cabin-door': [8, 27.4], // 小木屋门口，守林人和灯
  'bedroom-dark': [10, 3.5], // 回到家的小房间
};

const jobs = [];
plan.forEach((p, i) => jobs.push({kind: 'film', name: `cue/${String(i).padStart(2, '0')}`, frame: p.frame}));
PLATES.forEach((w) => jobs.push({kind: 'plate', name: `plate/${w}`, which: w}));
Object.entries(FILM).forEach(([n, [si, sec]]) => jobs.push({kind: 'film', name: `film/${n}`, frame: Math.round((starts[si] + sec) * timeline.fps)}));

const filmComp = await selectComposition({serveUrl, id: 'Film', inputProps: {subtitles: false}, browserExecutable});
for (const j of jobs) {
  if (only && !j.name.startsWith(only)) continue;
  const output = path.resolve('out/book_img', `${j.name}.png`);
  fs.mkdirSync(path.dirname(output), {recursive: true});
  if (j.kind === 'film') {
    await renderStill({composition: filmComp, serveUrl, output, frame: j.frame, inputProps: {subtitles: false}, scale, browserExecutable, imageFormat: 'png'});
  } else {
    const comp = await selectComposition({serveUrl, id: 'Plate', inputProps: {which: j.which}, browserExecutable});
    await renderStill({composition: comp, serveUrl, output, frame: 0, inputProps: {which: j.which}, scale, browserExecutable, imageFormat: 'png'});
  }
  console.log(j.name);
}
console.log('done');
