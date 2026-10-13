// 快速出静帧，用来检查画面：
//   node scripts/stills.mjs <合成ID>:<帧号,帧号,...>[@props的JSON] ...  [--scale=0.5] [--out=out/stills]
// 场景内时间： Film:s1+12.5,s4+9   （场景id前缀 + 秒数）
// 例：node scripts/stills.mjs Film:100,400 Sheet:0@'{"which":"rabbit"}'
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {sceneStarts} from '../src/schedule.mjs';
const timeline = JSON.parse(fs.readFileSync(path.resolve('src/timeline.json'), 'utf8'));
const starts = sceneStarts(timeline);

const args = process.argv.slice(2);
const opt = (k, d) => (args.find((a) => a.startsWith(`--${k}=`)) ?? `--${k}=${d}`).split('=')[1];
const scale = parseFloat(opt('scale', '0.5'));
const outDir = path.resolve(opt('out', 'out/stills'));
fs.mkdirSync(outDir, {recursive: true});
const jobs = args.filter((a) => !a.startsWith('--'));

const browserExecutable = process.env.REMOTION_BROWSER ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), onProgress: () => {}});
for (const job of jobs) {
  const [head, propsJson] = job.split('@');
  const [id, frames] = head.split(':');
  const inputProps = propsJson ? JSON.parse(propsJson) : {};
  const comp = await selectComposition({serveUrl, id, inputProps, browserExecutable});
  for (const f of frames.split(',')) {
    let frame;
    const m = /^([\w-]+?)\+([\d.]+)$/.exec(f); // 场景id+秒数，如 s1-lost+12.5
    if (m) {
      const idx = timeline.scenes.findIndex((sc) => sc.id.startsWith(m[1]));
      frame = Math.round((starts[idx] + parseFloat(m[2])) * timeline.fps);
    } else frame = f === 'last' ? comp.durationInFrames - 1 : parseInt(f, 10);
    const tag = propsJson ? '-' + Object.values(inputProps).join('_') : '';
    const output = path.join(outDir, `${id}${tag}-${m ? m[1] + '_' + m[2] : String(frame).padStart(5, '0')}.png`);
    const t0 = Date.now();
    await renderStill({composition: comp, serveUrl, output, frame, inputProps, scale, browserExecutable, imageFormat: 'png'});
    console.log(output, `${Date.now() - t0}ms`);
  }
}
