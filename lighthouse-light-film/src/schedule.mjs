// 字幕出现/停留时间的计算规则：渲染（Subtitle.tsx）和检查（scripts/check-subtitles.mjs）共用同一份。
// 英文版：按“词”数算停留时间，给 6~8 岁刚学会读的孩子留够时间。
export const norm = (t) => t.replace(/[“”"]/g, '').replace(/[‘’]/g, "'").replace(/\s+/g, ' ').trim();
/** 词数：含字母或数字的片段（NO BUSES TODAY. SNOW. = 4 个词） */
export const words = (t) => (t.match(/[A-Za-z0-9][A-Za-z0-9'’-]*/g) ?? []).length;
/** 把一条字幕排成 1~2 行：已有 \n 就照它；太长就在中间附近的空格处断开（优先在标点后）。渲染和检查共用。 */
export const wrap = (text, max = 36) => {
  const parts = text.split('\n');
  if (parts.length > 1) return parts;
  if (text.length <= max) return [text];
  let best = -1, bestScore = 1e9;
  for (let i = 4; i < text.length - 3; i++) {
    if (text[i] !== ' ') continue;
    const prev = text[i - 1];
    const score = Math.abs(i - text.length / 2) - (/[,.:;!?]/.test(prev) ? 6 : 0);
    if (score < bestScore) { bestScore = score; best = i; }
  }
  return best < 0 ? [text] : [text.slice(0, best), text.slice(best + 1)];
};
/** 至少要停多久：1.3 秒起读 + 每个词 0.55 秒（约每分钟 110 个词） */
export const minDur = (t) => 1.3 + 0.55 * words(t);
/** 实际停留 = 最短 + 0.3 秒余量（含淡入淡出） */
export const holdDur = (t) => minDur(t) + 0.3;

/**
 * 场景里每条字幕的出现时间 t、停留 d（场景内秒数）。
 * 第一条在 lead 秒后出现；每条之间默认静默 gap=0.7 秒；也可以用 at 把某条钉在场景内的某一秒（和画面里的动作对齐）。
 */
export function schedule(scene) {
  let t = scene.lead ?? 1.5;
  return scene.cues.map((c, i) => {
    const d = c.d ?? holdDur(c.text);
    if (i > 0) t += c.gap ?? 0.7;
    if (c.at != null) t = c.at;
    const out = {...c, t, d};
    t += d;
    return out;
  });
}

export const sceneStarts = (tl) => {
  const out = [];
  let s = 0;
  for (const sc of tl.scenes) {
    out.push(s);
    s += sc.len;
  }
  return out;
};
