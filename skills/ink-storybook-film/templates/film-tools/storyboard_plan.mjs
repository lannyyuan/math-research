// 分镜 PPT 的取帧计划：片头标题 1 张 + 每条字幕 1 张（取字幕停留 70% 处的画面，此时字幕已淡入、动作已展开）
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {schedule, sceneStarts} from '../src/schedule.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const starts = sceneStarts(tl);
const NAMES = {
  's0-title': '片头', 's1-lost': '雪夜迷路，看见山顶的灯', 's2-rabbit': '遇见问号', 's3-turtle': '遇见慢慢',
  's4-river': '冰河落水，被白鹿救起', 's5-fire': '在火堆边说起家', 's6-wolf': '帮小狼找到妈妈', 's7-thaw': '冰雪化开',
  's8-summit': '到了山顶，灯不是家', 's9-farewell': '和伙伴们告别', 's10-window': '在自己窗边点灯',
};
const tc = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
const plan = [{scene: 's0-title', sceneName: NAMES['s0-title'], text: tl.title, t: 2.8, frame: Math.round(2.8 * tl.fps), tc: '0:02'}];
tl.scenes.forEach((sc, i) => {
  schedule(sc).forEach((c, k) => {
    const g = starts[i] + c.t + c.d * 0.7;
    plan.push({scene: sc.id, sceneName: NAMES[sc.id], idx: k + 1, text: c.text, t: g, frame: Math.round(g * tl.fps), tc: tc(starts[i] + c.t)});
  });
});
fs.mkdirSync(path.join(root, 'out'), {recursive: true});
fs.writeFileSync(path.join(root, 'out/storyboard_plan.json'), JSON.stringify(plan, null, 1));
console.log(`共 ${plan.length} 张画面`);
console.log(plan.map((p) => p.frame).join(','));
