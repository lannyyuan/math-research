// 字幕排程：由每条字幕的 gap（前面的静默）和停留规则，算出绝对出现时间。
// Film.tsx 与 scripts/check-subtitles.mjs 共用这一份规则。
const QUOTES = /["“”‘’「」『』'\s]/g;
export const norm = (s) => s.replace(QUOTES, '');
const HAN = /\p{Script=Han}/u;

/** 阅读单位：汉字 1，标点 0.25 */
export const readUnits = (text) => {
  let n = 0;
  for (const ch of norm(text)) n += HAN.test(ch) ? 1 : 0.25;
  return n;
};
/** 6~8 岁孩子读完所需的最短停留：1.6 秒 + 每个汉字 0.30 秒 */
export const minDur = (text) => Math.ceil((1.6 + 0.3 * readUnits(text)) * 10) / 10;
/** 实际停留 = 最短停留 + 0.2 秒余量（也可在 JSON 里用 d 覆盖，但不得低于最短停留） */
export const holdDur = (cue) => cue.d ?? Math.round((minDur(cue.text) + 0.2) * 10) / 10;

/** @returns {{t:number,d:number,text:string}[]}  t 为相对场景开头的秒数 */
export const schedule = (scene) => {
  let cursor = 0;
  return scene.cues.map((c) => {
    const t = Math.round((cursor + (c.gap ?? 0.6)) * 10) / 10;
    const d = holdDur(c);
    cursor = t + d;
    return {t, d, text: c.text};
  });
};

/** 场景起点（秒） */
export const sceneStarts = (tl) => {
  let s = 0;
  return tl.scenes.map((sc) => {
    const o = s;
    s += sc.len;
    return o;
  });
};
