// 字幕与时间线检查：  node scripts/check-subtitles.mjs
//  1. 每条字幕必须是故事原文（story/film_source.txt）正文里的连续片段，一个字都不改。
//     行首是 # 或【的行是批注/画面提示，不算正文，不能当字幕。
//     唯一的例外：结尾字幕“下一个故事，等你来讲。”——任务书指定它是最后一句字幕，它在原文里只出现在【44】的画面提示行里；
//     时间线里用 "exception": true 标出，检查器会确认这一句确实原样出现在原文里（提示行），并且只允许这一条例外。
//  2. 每条最多两行，每行 ≤ 18 个字（含标点）；停留 ≥ 1.5 秒 + 0.3 秒/字（含标点）。
//  3. 字幕之间留 ≥ 0.3 秒；字幕不能越过场景结尾。
//  4. 总时长在 4:30 ~ 5:00 之间。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {flat, chars, wrap, minDur, schedule, sceneStarts, MAX_LINE} from '../src/schedule.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const lines = fs.readFileSync(path.join(root, 'story/film_source.txt'), 'utf8').split('\n');
const bodyLines = lines.filter((l) => l.trim() && !l.startsWith('#') && !l.startsWith('【')).map(flat);
const bodyAll = bodyLines.join('');
const promptLines = lines.filter((l) => l.startsWith('【')).map(flat);

let errors = 0;
const err = (m) => { errors++; console.log('  ✗ ' + m); };
const rows = [];
let total = 0, nCues = 0, nChars = 0, nExc = 0;
const used = new Set();
for (const sc of tl.scenes) {
  const sched = schedule(sc);
  let covered = 0;
  sched.forEach((c, i) => {
    const f = flat(c.text);
    if (c.exception) {
      nExc++;
      if (!promptLines.some((p) => p.includes(f))) err(`[${sc.id}#${i}] 例外字幕也必须出现在原文里: 「${c.text}」`);
    } else if (!bodyLines.some((b) => b.includes(f))) err(`[${sc.id}#${i}] 不是正文里同一行的连续片段: 「${c.text}」`);
    const ls = wrap(c.text);
    if (ls.length > 2) err(`[${sc.id}#${i}] 超过 2 行`);
    for (const l of ls) if ([...flat(l)].length > MAX_LINE) err(`[${sc.id}#${i}] 单行超过 ${MAX_LINE} 个字: 「${l}」`);
    if ((c.gap ?? 0.5) < 0.3) err(`[${sc.id}#${i}] gap < 0.3s`);
    if (c.d != null && c.d < minDur(c.text)) err(`[${sc.id}#${i}] 停留太短 ${c.d}s < ${minDur(c.text)}s`);
    if (i > 0 && c.t < sched[i - 1].t + sched[i - 1].d + 0.3 - 1e-6) err(`[${sc.id}#${i}] 和上一条的间隔不足 0.3s`);
    if (used.has(f)) err(`[${sc.id}#${i}] 重复的字幕: 「${c.text}」`);
    used.add(f);
    covered += c.d;
    nCues++; nChars += chars(c.text);
  });
  const last = sched.at(-1);
  const need = last ? last.t + last.d + 0.6 : 0;
  if (need > sc.len + 1e-6) err(`[${sc.id}] 场景太短：字幕要到 ${need.toFixed(1)}s（含 0.6s 尾巴），场景只有 ${sc.len}s`);
  rows.push({scene: sc.id, len: sc.len, cues: sc.cues.length, 'subtitled(s)': covered.toFixed(1), 'min len': need.toFixed(1), ends: last ? (last.t + last.d).toFixed(1) : '-'});
  total += sc.len;
}
// 字幕在原文里的顺序必须和故事一致
let pos = -1;
for (const sc of tl.scenes) for (const c of sc.cues) {
  if (c.exception) continue;
  const f = flat(c.text);
  const p = bodyAll.indexOf(f, Math.max(pos, 0));
  if (p < 0) err(`字幕顺序和原文不一致: 「${c.text}」`); else pos = p + f.length - 1;
}
if (nExc > 1) err('只允许一条例外字幕');
console.table(rows);
console.log('场景起点(秒):', sceneStarts(tl).join(', '));
console.log(`总时长 ${total}s = ${Math.floor(total / 60)}:${String(Math.round(total % 60)).padStart(2, '0')}   (要求 4:30~5:00 = 270~300s)`);
console.log(`字幕 ${nCues} 条，共 ${nChars} 字，其中例外 ${nExc} 条`);
if (total < 270 || total > 300) err('总时长不在 4:30~5:00 之间');
const set = new Set(); for (const sc of tl.scenes) for (const c of sc.cues) for (const ch of flat(c.text)) set.add(ch);
fs.writeFileSync(path.join(root, 'story/subtitle-chars.txt'), [...set].sort().join('') + '\n');
console.log(errors ? `\n未通过：${errors} 个问题` : '\n全部通过 ✓ 每条字幕都是原文片段（含 1 条指定的例外），停留时间足够');
process.exit(errors ? 1 : 0);
