// 字幕与时间线检查：  node scripts/check-subtitles.mjs
//
//  1. 每条字幕必须是原文（story/source.md）里的连续片段（忽略引号和空白；首尾的逗号顿号可去掉）。
//     —— 不能新造句子。
//  2. 每条字幕停留时间 ≥ 1.6 秒 + 0.30 秒 × 汉字数（标点按 0.25 个字），让 6~8 岁孩子读完。
//  3. 单行 ≤ 18 个字符，最多 2 行；字幕之间留 ≥ 0.3 秒间隙；字幕不能越过场景结尾。
//  4. 总时长在 4:00 ~ 5:00 之间。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {norm, minDur, schedule, sceneStarts} from '../src/schedule.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const src = norm(fs.readFileSync(path.join(root, 'story/source.md'), 'utf8'));
const HAN = /\p{Script=Han}/u;

let errors = 0;
const err = (m) => {
  errors++;
  console.log('  ✗ ' + m);
};

if (!src.includes(norm(tl.title))) err(`标题不在原文里: ${tl.title}`);

const chars = new Set(tl.title);
const rows = [];
let total = 0;
for (const sc of tl.scenes) {
  const sched = schedule(sc);
  let covered = 0;
  sc.cues.forEach((c, i) => {
    const lines = c.text.split('\n');
    const flat = norm(c.text);
    const trimmed = flat.replace(/^[，、；：]+|[，、；：]+$/g, '');
    if (!src.includes(trimmed)) err(`[${sc.id}#${i}] 不是原文片段: 「${c.text}」`);
    if (lines.length > 2) err(`[${sc.id}#${i}] 超过 2 行`);
    for (const l of lines) if ([...l].length > 18) err(`[${sc.id}#${i}] 单行超过 18 字: 「${l}」`);
    if ((c.gap ?? 0.6) < 0.3) err(`[${sc.id}#${i}] gap < 0.3s`);
    if (c.d != null && c.d < minDur(c.text)) err(`[${sc.id}#${i}] 停留太短 ${c.d}s < ${minDur(c.text)}s`);
    covered += sched[i].d;
    for (const ch of flat) chars.add(ch);
  });
  const last = sched.at(-1);
  const need = last ? last.t + last.d + 0.3 : 0;
  if (need > sc.len + 1e-6) err(`[${sc.id}] 场景太短：字幕要到 ${need.toFixed(1)}s，场景只有 ${sc.len}s`);
  rows.push({scene: sc.id, len: sc.len, cues: sc.cues.length, subtitled: covered.toFixed(1), 'min len': need.toFixed(1), ends: last ? (last.t + last.d).toFixed(1) : '-'});
  total += sc.len;
}
console.table(rows);
const starts = sceneStarts(tl);
console.log('场景起点(秒):', starts.join(', '));
console.log(`总时长 ${total}s = ${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}   (要求 240~300s)`);
if (total < 240 || total > 300) err('总时长不在 4~5 分钟之间');

fs.writeFileSync(path.join(root, 'story/subtitle-chars.txt'), [...chars].sort().join(''));
console.log(`字幕共用到 ${[...chars].filter((c) => HAN.test(c)).length} 个不同汉字 → story/subtitle-chars.txt`);
console.log(errors ? `\n未通过：${errors} 个问题` : '\n全部通过 ✓ 每条字幕都是原文片段，停留时间足够');
process.exit(errors ? 1 : 0);
