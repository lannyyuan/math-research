/**
 * The single source of truth for "what happens when" in the gasoline-car video.
 * Segment lengths start from the storyboard targets and stretch if the real
 * narration is longer (narration wins). Every visual event is expressed in
 * seconds derived from here, and every animation is a pure function of the
 * current frame → renders are reproducible.
 */
import type { CamKey, CamPose } from "../lib/camera";

export type VoiceLine = { text: string; start: number; end: number };
export type VoiceSegment = {
  file: string;
  duration: number;
  lines: VoiceLine[];
  words: { text: string; start: number; end: number }[];
};
export type VoiceTiming = { voice: string; segments: Record<string, VoiceSegment> };

export const SEG_ORDER = ["title", "tank", "engine", "gearbox", "support", "explode", "end"] as const;
export type SegId = (typeof SEG_ORDER)[number];

/** Storyboard target lengths (seconds). */
const TARGET: Record<SegId, number> = {
  title: 2,
  tank: 10,
  engine: 16,
  gearbox: 12,
  support: 12,
  explode: 16,
  end: 2,
};

/** Earliest time (relative to segment start) each narration line may start; null = right after the previous one. */
const LINE_AT: Partial<Record<SegId, (number | null)[]>> = {
  tank: [0.8, 2.6],
  engine: [2.4, 5.0, null, null],
  gearbox: [1.6, 5.0, 7.6],
  support: [0.6, 3.8, 6.8, 9.8],
  explode: [1.0, 8.6],
};
const TAIL = 0.6;
const MIN_TOTAL = 60;
const MAX_TOTAL = 80;

export type ScheduledLine = {
  seg: SegId;
  idx: number;
  text: string;
  file: string;
  /** Absolute time the audio clip is placed at. */
  clipAt: number;
  /** Portion of the source file played. */
  srcFrom: number;
  srcTo: number;
  /** Absolute times the words are actually heard. */
  speechStart: number;
  speechEnd: number;
};

export const buildTimeline = (voice: VoiceTiming, fps = 30) => {
  const seg = {} as Record<SegId, { start: number; end: number }>;
  const lines: ScheduledLine[] = [];
  let cursor = 0;
  for (const id of SEG_ORDER) {
    const start = cursor;
    let need = TARGET[id];
    const v = voice.segments[id];
    if (v) {
      const at = LINE_AT[id] ?? [];
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
        const srcFrom = cuts[i];
        const srcTo = cuts[i + 1];
        lines.push({
          seg: id,
          idx: i,
          text: v.lines[i].text,
          file: v.file,
          clipAt,
          srcFrom,
          srcTo,
          speechStart: clipAt + lead,
          speechEnd: clipAt + (v.lines[i].end - srcFrom),
        });
        prevClipEnd = clipAt + (srcTo - srcFrom);
      }
      need = Math.max(need, lines[lines.length - 1].speechEnd + TAIL - start);
    }
    seg[id] = { start, end: start + need };
    cursor = start + need;
  }
  // snap segment boundaries to whole frames
  for (const id of SEG_ORDER) {
    seg[id].start = Math.round(seg[id].start * fps) / fps;
    seg[id].end = Math.round(seg[id].end * fps) / fps;
  }
  const total = seg.end.end;
  if (total < MIN_TOTAL || total > MAX_TOTAL) {
    throw new Error(`Timeline is ${total.toFixed(2)}s — must stay within ${MIN_TOTAL}-${MAX_TOTAL}s`);
  }

  const L = (s: SegId, i: number) => {
    const l = lines.find((x) => x.seg === s && x.idx === i);
    if (!l) throw new Error(`missing narration line ${s}[${i}]`);
    return l;
  };
  // time of the "砰" in the engine line → a cylinder fires exactly then
  const engineVoice = voice.segments.engine;
  const pengWord = engineVoice.words.find((w) => w.text.includes("砰"));
  const engLine1 = L("engine", 1);
  const peng = pengWord ? engLine1.clipAt + (pengWord.start - engLine1.srcFrom) + 0.05 : engLine1.speechStart + 1;

  const T = seg.tank.start;
  const E = seg.engine.start;
  const G = seg.gearbox.start;
  const S = seg.support.start;
  const X = seg.explode.start;
  const N = seg.end.start;

  const ev = {
    // body
    xrayOn: [T + 0.05, T + 0.95] as const,
    xrayOff: [N - 0.7, N + 0.15] as const,
    // tank
    tankHL: L("tank", 0).speechStart - 0.25,
    fuelFlow: L("tank", 1).speechStart,
    fuelFlowEnd: E + 1.6,
    // engine
    engineHL: L("engine", 0).speechStart - 0.15,
    peng,
    pistonHL: L("engine", 2).speechStart - 0.1,
    crankHL: L("engine", 3).speechStart - 0.1,
    engineExtras: L("engine", 3).speechEnd + 0.5,
    firingPanel: [L("engine", 1).speechStart - 0.3, G + 0.6] as const,
    engineSlowMo: [E + 0.6, E + 2.0] as const,
    // gearbox
    gearboxHL: L("gearbox", 0).speechStart - 0.15,
    driveStart: G + 2.0,
    shift1: L("gearbox", 0).speechEnd - 0.35,
    shift2: L("gearbox", 1).speechEnd + 0.45,
    shiftDur: 0.5,
    wheelsShow: L("gearbox", 1).speechStart - 0.4,
    powerArrows: [G + 2.0, S + 0.4] as const,
    gearPanel: [L("gearbox", 0).speechStart - 0.2, S + 0.2] as const,
    cruiseReached: G + 9.4,
    // support systems
    radiatorHL: L("support", 0).speechStart - 0.2,
    oilHL: L("support", 1).speechStart - 0.2,
    exhaustHL: L("support", 2).speechStart - 0.2,
    allHL: L("support", 3).speechStart - 0.1,
    exhaustCam: L("support", 2).speechStart - 0.9,
    // exploded view
    stop: [X, X + 0.9] as const,
    explodeOut: [X + 1.2, X + 3.6] as const,
    labelsIn: X + 3.2,
    counter: [X + 3.4, X + 7.6] as const,
    labelsOut: X + 8.5,
    merge: [X + 8.8, X + 11.2] as const,
    restart: X + 11.6,
    driveAway: X + 12.2,
    // end
    smile: N - 0.4,
  };

  const CAM: Record<string, CamPose> = {
    hero: { pos: [6.2, 1.9, 7.0], target: [0.15, 0.72, 0], fov: 30 },
    side: { pos: [0.05, 1.45, 8.4], target: [0.05, 0.68, 0], fov: 30 },
    sideLow: { pos: [0.1, 1.2, 8.0], target: [0.1, 0.66, 0], fov: 30 },
    engine: { pos: [2.75, 1.3, 0.95], target: [1.47, 0.6, 0.18], fov: 30 },
    engineDrift: { pos: [2.8, 1.36, 0.72], target: [1.47, 0.6, 0.16], fov: 30 },
    gearbox: { pos: [2.22, 1.08, -0.42], target: [1.43, 0.42, -0.29], fov: 30 },
    axle: { pos: [3.9, 2.3, -2.4], target: [1.2, 0.42, 0.0], fov: 32 },
    support: { pos: [3.7, 1.55, 2.6], target: [1.45, 0.55, 0.0], fov: 32 },
    exhaust: { pos: [-4.4, 1.9, 4.9], target: [0.1, 0.45, 0], fov: 34 },
    explode: { pos: [3.85, 2.75, 6.3], target: [1.0, 0.78, 0.0], fov: 36 },
    explodeDrift: { pos: [3.7, 2.8, 6.4], target: [1.0, 0.78, 0.0], fov: 36 },
    endHero: { pos: [6.6, 1.7, 5.4], target: [0.3, 0.7, 0], fov: 30 },
  };

  const keys: CamKey[] = [
    { t: 0, pose: CAM.hero },
    { t: seg.title.end - 0.2, pose: CAM.side },
    { t: E, pose: CAM.side },
    { t: E + 2.2, pose: CAM.engine },
    { t: G - 0.2, pose: CAM.engineDrift },
    { t: G + 1.6, pose: CAM.gearbox },
    { t: ev.wheelsShow, pose: CAM.gearbox },
    { t: ev.wheelsShow + 1.6, pose: CAM.axle },
    { t: S - 0.2, pose: CAM.axle },
    { t: S + 1.2, pose: CAM.support },
    { t: ev.exhaustCam, pose: CAM.support },
    { t: ev.exhaustCam + 1.4, pose: CAM.exhaust },
    { t: X, pose: CAM.exhaust },
    { t: X + 1.6, pose: CAM.explode },
    { t: ev.merge[1], pose: CAM.explodeDrift },
    { t: N - 0.9, pose: CAM.explodeDrift },
    { t: N + 0.9, pose: CAM.endHero },
  ];

  return {
    fps,
    total,
    totalFrames: Math.round(total * fps),
    seg,
    lines,
    ev,
    camKeys: keys,
  };
};

export type Timeline = ReturnType<typeof buildTimeline>;
