// 从成片按“每条字幕的中点”抽帧（含场景编号），供联系表检查： node scripts/qa_frames.mjs dist/lighthouse-light.mp4 out/qa
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import {schedule, sceneStarts} from '../src/schedule.mjs';
const [mp4, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, {recursive: true});
const tl = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url), 'utf8'));
const st = sceneStarts(tl);
tl.scenes.forEach((sc, i) => {
  schedule(sc).forEach((c, j) => {
    const t = (st[i] + c.t + Math.min(c.d / 2, 2.2)).toFixed(2);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', t, '-i', mp4, '-frames:v', '1', '-vf', 'scale=640:-1', `${outDir}/${sc.id.split('-')[0]}_${String(j).padStart(2, '0')}.png`]);
  });
});
console.log('done');
