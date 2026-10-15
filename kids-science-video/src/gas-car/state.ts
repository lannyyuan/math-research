/** Per-frame scene state — a pure function of (timeline, frame). Shared by 3D scene, overlay and checks. */
import { ramp, smooth, smoother, window } from "../lib/anim";
import { cameraAt } from "../lib/camera";
import type { Drive, DriveState } from "./mechanics";
import { PART_IDS, PARTS, WHEEL_EXPLODE, type PartId } from "./parts";
import type { Timeline } from "./timeline";

type V3 = readonly [number, number, number];

export type SceneState = {
  t: number;
  frame: number;
  drive: DriveState;
  xray: number;
  hl: Record<PartId, number>;
  explode: number;
  fuelFlow: number; // seconds since the fuel started flowing (<0 = not yet)
  fuelVis: number;
  wind: number;
  oilFlow: number;
  oilVis: number;
  exhaustHeat: number;
  puffs: number;
  powerArrows: number;
  smile: number;
  /** Opacity multipliers that ghost parts standing in front of the current focus. */
  ghost: Record<PartId | "wheelFL" | "wheelFR", number>;
};

export const sceneState = (tl: Timeline, drive: Drive, frame: number): SceneState => {
  const t = frame / tl.fps;
  const { ev, seg } = tl;
  const E = seg.engine.start;
  const G = seg.gearbox.start;
  const S = seg.support.start;
  const X = seg.explode.start;

  const xray = smooth(ramp(t, ev.xrayOn[0], ev.xrayOn[1])) * (1 - smooth(ramp(t, ev.xrayOff[0], ev.xrayOff[1])));
  const explode =
    smoother(ramp(t, ev.explodeOut[0], ev.explodeOut[1])) * (1 - smoother(ramp(t, ev.merge[0], ev.merge[1])));

  const all = Math.max(window(t, ev.allHL, S + 12, 0.25, 0.4) * (t < X + 0.4 ? 1 : 0), 0);
  const explodeGlow = 0.3 * window(t, ev.labelsIn, ev.labelsOut + 0.3, 0.5, 0.5);
  const hl = {} as Record<PartId, number>;
  const set = (id: PartId, v: number) => (hl[id] = Math.min(1, Math.max(v, explodeGlow)));
  set("fuelTank", window(t, ev.tankHL, E + 0.8, 0.35, 0.6));
  set("fuelLine", window(t, ev.fuelFlow - 0.2, E + 0.8, 0.35, 0.6));
  set("block", 0.55 * window(t, ev.engineHL, ev.pistonHL + 0.2, 0.35, 0.5));
  set("pistons", window(t, ev.pistonHL, G + 0.4, 0.3, 0.5));
  set("crankshaft", window(t, ev.crankHL, G + 0.4, 0.3, 0.5));
  set("camValves", 0.85 * window(t, ev.engineExtras, G + 0.4, 0.3, 0.5));
  set("sparkPlugs", 0.85 * window(t, ev.engineExtras + 0.4, G + 0.4, 0.3, 0.5));
  set("intake", 0);
  set("gearbox", window(t, ev.gearboxHL, S + 0.3, 0.3, 0.5));
  set("halfShafts", window(t, ev.wheelsShow, S + 0.3, 0.3, 0.5));
  set("wheels", window(t, ev.wheelsShow, S + 0.3, 0.3, 0.5));
  set("radiator", Math.max(window(t, ev.radiatorHL, ev.oilHL + 0.1, 0.3, 0.4), all));
  set("oil", Math.max(window(t, ev.oilHL, ev.exhaustHL + 0.1, 0.3, 0.4), all));
  set("exhaustManifold", Math.max(window(t, ev.exhaustHL, X + 0.4, 0.3, 0.5), all));
  set("exhaustPipe", Math.max(window(t, ev.exhaustHL, X + 0.4, 0.3, 0.5), all));

  return {
    t,
    frame,
    drive: drive.at(frame),
    xray,
    hl,
    explode,
    fuelFlow: t - ev.fuelFlow,
    fuelVis: window(t, ev.fuelFlow, ev.fuelFlowEnd, 0.3, 0.6),
    wind: window(t, ev.radiatorHL, ev.oilHL + 0.3, 0.4, 0.5),
    oilFlow: t - ev.oilHL,
    oilVis: window(t, ev.oilHL, ev.exhaustHL + 0.6, 0.3, 0.5),
    exhaustHeat: window(t, ev.exhaustHL, X + 0.6, 0.6, 0.6),
    puffs: window(t, ev.exhaustHL + 0.3, X + 0.8, 0.3, 0.6),
    powerArrows: window(t, ev.powerArrows[0], ev.powerArrows[1], 0.4, 0.5),
    smile: smooth(ramp(t, ev.smile, ev.smile + 0.6)),
    ghost: ghostAt(tl, t),
  };
};

const ghostAt = (tl: Timeline, t: number): SceneState["ghost"] => {
  const { ev, seg } = tl;
  const E = seg.engine.start;
  const G = seg.gearbox.start;
  const S = seg.support.start;
  const fEngine = window(t, E + 0.5, G + 0.6, 1.2, 0.9);
  const fGear = window(t, G + 0.3, ev.wheelsShow + 0.7, 0.9, 0.7);
  const fAxle = window(t, ev.wheelsShow + 0.4, S + 0.8, 0.8, 0.7);
  const fOil = window(t, ev.oilHL - 0.3, ev.exhaustHL + 0.2, 0.4, 0.4);
  const g = {} as SceneState["ghost"];
  for (const id of PART_IDS) g[id] = 1;
  g.radiator = 1 - Math.max(0.85 * Math.max(fEngine, fGear), 0.6 * fAxle, 0.6 * fOil);
  g.fuelTank = 1 - 0.85 * fEngine;
  g.fuelLine = 1 - 0.4 * fEngine;
  g.exhaustManifold = 1 - Math.max(0.55 * fEngine, 0.5 * fGear);
  g.intake = 1 - 0.3 * fEngine;
  g.wheelFL = 1 - Math.max(0.5 * fGear, 0.5 * fEngine);
  g.block = 1 - 0.35 * fGear;
  g.pistons = 1 - 0.5 * fGear;
  g.camValves = 1 - 0.4 * fGear;
  g.sparkPlugs = 1 - 0.4 * fGear;
  g.exhaustPipe = 1 - 0.6 * fGear;
  g.wheelFR = 1 - 0.55 * fEngine;
  return g;
};

export const cameraPose = (tl: Timeline, t: number) => cameraAt(tl.camKeys, t);

/** Explode offset of a part at amount e (0..1). */
export const explodeOffset = (id: PartId, e: number): V3 => {
  const o = PARTS[id].explode;
  return [o[0] * e, o[1] * e, o[2] * e];
};

/** Label anchor in world space at the current explode amount. */
export const labelAnchor = (id: PartId, e: number): V3 => {
  const a = PARTS[id].anchor;
  const o = id === "wheels" ? WHEEL_EXPLODE.FR : PARTS[id].explode;
  return [a[0] + o[0] * e, a[1] + o[1] * e, a[2] + o[2] * e];
};

export const ALL_PARTS = PART_IDS;
