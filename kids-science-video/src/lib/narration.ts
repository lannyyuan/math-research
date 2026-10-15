/**
 * Generic narration-driven timeline builder (same rules the gasoline-car
 * timeline uses): each segment keeps its storyboard length unless its spoken
 * lines need more; lines can be pinned to earliest start times; audio is cut
 * between lines (in the silences) so each line can be placed independently.
 */
export type VoiceLine = { text: string; start: number; end: number };
export type VoiceWord = { text: string; start: number; end: number };
export type VoiceSegment = { file: string; duration: number; lines: VoiceLine[]; words: VoiceWord[] };
export type VoiceTiming = { voice: string; segments: Record<string, VoiceSegment> };

export type ScheduledLine<S extends string> = {
  seg: S;
  idx: number;
  text: string;
  file: string;
  clipAt: number;
  srcFrom: number;
  srcTo: number;
  speechStart: number;
  speechEnd: number;
};

export const scheduleNarration = <S extends string>(opts: {
  order: readonly S[];
  target: Record<S, number>;
  lineAt: Partial<Record<S, (number | null)[]>>;
  voice: VoiceTiming;
  fps: number;
  tail?: number;
  minTotal?: number;
  maxTotal?: number;
}) => {
  const { order, target, lineAt, voice, fps, tail = 0.6, minTotal = 60, maxTotal = 80 } = opts;
  const seg = {} as Record<S, { start: number; end: number }>;
  const lines: ScheduledLine<S>[] = [];
  let cursor = 0;
  for (const id of order) {
    const start = cursor;
    let need = target[id];
    const v = voice.segments[id];
    if (v) {
      const at = lineAt[id] ?? [];
      const n = v.lines.length;
      const cuts = [0];
      for (let i = 1; i < n; i++) cuts.push((v.lines[i - 1].end + v.lines[i].start) / 2);
      cuts.push(v.duration);
      let prevClipEnd = start;
      for (let i = 0; i < n; i++) {
        const lead = v.lines[i].start - cuts[i];
        const desired = at[i] ?? null;
        let clipAt = desired === null ? prevClipEnd : start + desired - lead;
        clipAt = Math.max(clipAt, prevClipEnd);
        lines.push({
          seg: id,
          idx: i,
          text: v.lines[i].text,
          file: v.file,
          clipAt,
          srcFrom: cuts[i],
          srcTo: cuts[i + 1],
          speechStart: clipAt + lead,
          speechEnd: clipAt + (v.lines[i].end - cuts[i]),
        });
        prevClipEnd = clipAt + (cuts[i + 1] - cuts[i]);
      }
      need = Math.max(need, lines[lines.length - 1].speechEnd + tail - start);
    }
    seg[id] = { start, end: start + need };
    cursor = start + need;
  }
  for (const id of order) {
    seg[id].start = Math.round(seg[id].start * fps) / fps;
    seg[id].end = Math.round(seg[id].end * fps) / fps;
  }
  const total = seg[order[order.length - 1]].end;
  if (total < minTotal || total > maxTotal) throw new Error(`Timeline is ${total.toFixed(2)}s — must stay within ${minTotal}-${maxTotal}s`);
  const line = (s: S, i: number) => {
    const l = lines.find((x) => x.seg === s && x.idx === i);
    if (!l) throw new Error(`missing narration line ${s}[${i}]`);
    return l;
  };
  /** Absolute time a given word (first occurrence containing `text`) is spoken in segment `s`. */
  const wordAt = (s: S, text: string) => {
    const v = voice.segments[s];
    const w = v.words.find((x) => x.text.includes(text));
    if (!w) throw new Error(`word ${text} not found in ${s}`);
    const l = lines.find((x) => x.seg === s && w.start >= x.srcFrom - 1e-6 && w.start < x.srcTo);
    if (!l) throw new Error(`word ${text} outside lines`);
    return l.clipAt + (w.start - l.srcFrom);
  };
  return { seg, lines, total, totalFrames: Math.round(total * fps), line, wordAt };
};
