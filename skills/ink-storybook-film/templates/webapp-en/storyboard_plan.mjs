// 影片 → 绘本：每条字幕取“停留 70% 处”的画面（字幕已淡入、动作已展开）。输出 out/storyboard_plan.json
//   [ {scene, sceneName, idx, text, tc, frame, t}, ... ]   第 0 项是片头
import fs from 'node:fs';
import {schedule, sceneStarts} from '../src/schedule.mjs';
const tl = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url), 'utf8'));
const st = sceneStarts(tl);
const tc = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
const out = [{scene: 's0-title', sceneName: 'Title', idx: 0, text: tl.title, t: 3, tc: tc(3), frame: Math.round(3 * tl.fps)}];
tl.scenes.forEach((sc, i) => {
  schedule(sc).forEach((c, j) => {
    const t = st[i] + c.t + 0.7 * c.d;
    out.push({scene: sc.id, sceneName: sc.name, idx: j, text: c.text, t: +t.toFixed(2), tc: tc(st[i] + c.t), frame: Math.round(t * tl.fps)});
  });
});
fs.mkdirSync('out', {recursive: true});
fs.writeFileSync('out/storyboard_plan.json', JSON.stringify(out, null, 1));
console.log(`storyboard_plan.json: ${out.length} 项（含片头）`);
