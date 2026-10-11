// 字幕与时间线检查：  node scripts/check-subtitles.mjs
//  1. 每条字幕必须是故事原文里的连续片段（只能截取，不能新造句子）；“---”以后的统计附录不算故事。
//  2. 每条停留时间 ≥ 1.3 秒 + 0.55 秒 × 词数（刚学认字的孩子，约每分钟 110 个词）。
//  3. 单行 ≤ 38 个字符，最多 2 行；字幕之间留 ≥ 0.3 秒；字幕不能越过场景结尾。
//  4. 总时长在 3:00 ~ 5:00 之间。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {norm, words, wrap, minDur, schedule, sceneStarts} from '../src/schedule.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
let raw = fs.readFileSync(path.join(root, 'story/source.md'), 'utf8');
const cut = raw.search(/^---\s*$/m);
if (cut >= 0) raw = raw.slice(0, cut); // 去掉末尾的统计附录
const src = norm(raw);

let errors = 0;
const err = (m) => { errors++; console.log('  ✗ ' + m); };
const rows = [];
let total = 0, nCues = 0, nWords = 0;
const vocab = new Set();
for (const sc of tl.scenes) {
  const sched = schedule(sc);
  let covered = 0;
  sched.forEach((c, i) => {
    const flat = norm(c.text);
    if (!src.includes(flat)) err(`[${sc.id}#${i}] 不是原文片段: 「${c.text}」`);
    const lines = wrap(c.text);
    if (lines.length > 2) err(`[${sc.id}#${i}] 超过 2 行`);
    for (const l of lines) if ([...l].length > 38) err(`[${sc.id}#${i}] 单行超过 38 个字符: 「${l}」`);
    if ((c.gap ?? 0.7) < 0.3) err(`[${sc.id}#${i}] gap < 0.3s`);
    if (c.d != null && c.d < minDur(c.text)) err(`[${sc.id}#${i}] 停留太短 ${c.d}s < ${minDur(c.text).toFixed(2)}s`);
    if (i > 0 && c.t < sched[i - 1].t + sched[i - 1].d + 0.3 - 1e-6) err(`[${sc.id}#${i}] 和上一条的间隔不足 0.3s`);
    covered += c.d;
    nCues++; nWords += words(c.text);
    for (const w of c.text.toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g) ?? []) vocab.add(w);
  });
  const last = sched.at(-1);
  const need = last ? last.t + last.d + 0.6 : 0;
  if (need > sc.len + 1e-6) err(`[${sc.id}] 场景太短：字幕要到 ${need.toFixed(1)}s（含 0.6s 尾巴），场景只有 ${sc.len}s`);
  rows.push({scene: sc.id, len: sc.len, cues: sc.cues.length, subtitled: covered.toFixed(1), 'min len': need.toFixed(1), ends: last ? (last.t + last.d).toFixed(1) : '-'});
  total += sc.len;
}
console.table(rows);
console.log('场景起点(秒):', sceneStarts(tl).join(', '));
console.log(`总时长 ${total}s = ${Math.floor(total / 60)}:${String(Math.round(total % 60)).padStart(2, '0')}   (要求 180~300s)`);
console.log(`字幕 ${nCues} 条，${nWords} 个词（含重复），${vocab.size} 个不同的词`);
if (total < 180 || total > 300) err('总时长不在 3~5 分钟之间');
fs.writeFileSync(path.join(root, 'story/subtitle-words.txt'), [...vocab].sort().join('\n') + '\n');
console.log(errors ? `\n未通过：${errors} 个问题` : '\n全部通过 ✓ 每条字幕都是原文片段，停留时间足够');
process.exit(errors ? 1 : 0);
