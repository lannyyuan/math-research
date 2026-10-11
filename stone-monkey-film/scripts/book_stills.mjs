// 绘本配图：node scripts/book_stills.mjs [--only=cue|plate] [--keys=kitchen,hall_king] [--scale=0.75]
//   cue/NN   ：影片的干净帧（不带字幕、不带声音），取 out/storyboard_plan.json（先 node scripts/storyboard_plan.mjs）里每条字幕“停留 70% 处”
//   plate/名 ：src/plates/Plate.tsx 里的 16 个补充插图（现成背景板 + 现成人物精灵）
// 输出到 out/book_img/{cue,plate}/*.png，然后 `python3 -X utf8 -I webapp/build.py` 就会换掉占位图。
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const args = process.argv.slice(2);
const opt = (k, d) => (args.find((a) => a.startsWith(`--${k}=`)) ?? `--${k}=${d}`).split('=')[1];
const only = opt('only', 'all'), scale = parseFloat(opt('scale', '0.75'));
const keys = opt('keys', '').split(',').filter(Boolean);
const browserExecutable = process.env.REMOTION_BROWSER ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), onProgress: () => {}});
const outRoot = path.resolve('out/book_img');

if (only === 'all' || only === 'cue') {
  const plan = JSON.parse(fs.readFileSync('out/storyboard_plan.json', 'utf8'));
  fs.mkdirSync(path.join(outRoot, 'cue'), {recursive: true});
  const inputProps = {subtitles: false, audio: false};
  const comp = await selectComposition({serveUrl, id: 'Film', inputProps, browserExecutable});
  for (let i = 1; i < plan.length; i++) {
    const key = String(i).padStart(2, '0');
    if (keys.length && !keys.includes(`cue/${key}`) && !keys.includes(key)) continue;
    await renderStill({composition: comp, serveUrl, output: path.join(outRoot, 'cue', `${key}.png`), frame: plan[i].frame, inputProps, scale, browserExecutable, imageFormat: 'png'});
    console.log(`cue/${key}  ${plan[i].scene}  t=${plan[i].t}s  ${plan[i].text}`);
  }
}
if (only === 'all' || only === 'plate') {
  fs.mkdirSync(path.join(outRoot, 'plate'), {recursive: true});
  const names = fs.readFileSync('src/plates/Plate.tsx', 'utf8').match(/^  ([a-z_]+): \{v: '/gm).map((s) => s.trim().split(':')[0]);
  for (const which of names) {
    if (keys.length && !keys.includes(which) && !keys.includes(`plate/${which}`)) continue;
    const inputProps = {which};
    const comp = await selectComposition({serveUrl, id: 'Plate', inputProps, browserExecutable});
    await renderStill({composition: comp, serveUrl, output: path.join(outRoot, 'plate', `${which}.png`), frame: 0, inputProps, scale, browserExecutable, imageFormat: 'png'});
    console.log(`plate/${which}`);
  }
}
