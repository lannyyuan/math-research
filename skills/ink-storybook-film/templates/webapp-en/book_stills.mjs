// 绘本网页要用的画面（1920×1080 PNG）：
//   cue/NN.png    影片每条字幕的干净画面（不带字幕）；cue/00 = 片头
//   film/cover    封面（片头画面，封面图 + 夜空补边）
//   plate/*.png   补充插图（Plate 合成）
//   node scripts/book_stills.mjs [--only=cue/|plate/|film/]
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const only = (process.argv.find((a) => a.startsWith('--only=')) ?? '--only=').split('=')[1];
const outDir = path.resolve('out/book_img');
const plan = JSON.parse(fs.readFileSync('out/storyboard_plan.json', 'utf8'));
const browserExecutable = process.env.REMOTION_BROWSER ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), onProgress: () => {}});
const film = await selectComposition({serveUrl, id: 'Film', inputProps: {subtitles: false, audio: false}, browserExecutable});
const jobs = [];
plan.forEach((c, i) => jobs.push({key: `cue/${String(i).padStart(2, '0')}`, comp: film, frame: c.frame, props: {subtitles: false, audio: false}}));
jobs.push({key: 'film/cover', comp: film, frame: Math.round(3 * 30), props: {subtitles: false, audio: false}});
for (const w of ['city', 'castle', 'castle_in', 'fairground', 'caravan', 'dream', 'spring', 'dinner', 'presents']) jobs.push({key: `plate/${w}`, comp: await selectComposition({serveUrl, id: 'Plate', inputProps: {which: w}, browserExecutable}), frame: 0, props: {which: w}});
for (const j of jobs) {
  if (only && !j.key.startsWith(only)) continue;
  const output = path.join(outDir, j.key + '.png');
  fs.mkdirSync(path.dirname(output), {recursive: true});
  await renderStill({composition: j.comp, serveUrl, output, frame: j.frame, inputProps: j.props, browserExecutable, imageFormat: 'png'});
  console.log(j.key);
}
