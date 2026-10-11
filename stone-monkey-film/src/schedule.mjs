// 字幕排程与规则：Subtitle.tsx（渲染）和 scripts/check-subtitles.mjs（检查）共用。
//  · 每条字幕最多两行，每行不超过 18 个字（标点也算一个字）；
//  · 停留时间至少 1.5 秒，再按每字加 0.3 秒（标点也算一个字）；实际停留再加 0.2 秒余量。
export const MAX_LINE = 18;
const SPACE = /\s+/g;
/** 去掉空白和换行后的文字（字幕和原文比对、数字数都用它） */
export const flat = (t) => t.replace(SPACE, '');
export const chars = (t) => [...flat(t)].length;
/** 至少要停多久：1.5 秒 + 每字 0.3 秒 */
export const minDur = (t) => Math.round((1.5 + 0.3 * chars(t)) * 100) / 100;
/** 实际停留 = 最短 + 0.2 秒余量（含淡入淡出） */
export const holdDur = (t) => Math.round((minDur(t) + 0.2) * 100) / 100;

const BREAK = /[，。：；！？、”）]/;
/** 排成 1~2 行：文字里已有 \n 就照它；超过一行的，在中间附近的标点后断开（两行都不超过 MAX_LINE）。 */
export const wrap = (text) => {
  const parts = text.split('\n');
  if (parts.length > 1) return parts;
  const cs = [...text];
  if (cs.length <= MAX_LINE) return [text];
  let best = -1, bestScore = 1e9;
  for (let i = 3; i < cs.length - 2; i++) {
    if (!BREAK.test(cs[i - 1])) continue;
    const score = Math.abs(i - cs.length / 2);
    if (score < bestScore) { bestScore = score; best = i; }
  }
  if (best < 0) best = Math.ceil(cs.length / 2);
  return [cs.slice(0, best).join(''), cs.slice(best).join('')];
};

/**
 * 场景里每条字幕的出现时间 t、停留 d（场景内秒数）。
 * 第一条在 lead 秒后出现；之后每条之间静默 gap（默认 0.5 秒）；也可以用 at 把某条钉在场景内的某一秒（和画面里的动作对齐）。
 */
export function schedule(scene) {
  let t = scene.lead ?? 1.5;
  return scene.cues.map((c, i) => {
    const d = c.d ?? holdDur(c.text);
    if (i > 0) t += c.gap ?? 0.5;
    if (c.at != null) t = c.at;
    const out = {...c, t: Math.round(t * 100) / 100, d};
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
