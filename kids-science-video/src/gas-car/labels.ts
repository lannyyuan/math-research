/** When/where every Chinese label appears in the gasoline-car video (one schedule → visuals + click sounds). */
import { easeOutBack, ramp, smooth } from "../lib/anim";
import type { Vec3 } from "../lib/camera";
import type { LabelItem } from "../components/LabelLayer";
import { COLORS } from "../style/theme";
import { ENG, GBX } from "./layout";
import { PART_IDS, PARTS } from "./parts";
import { labelAnchor, type SceneState } from "./state";
import type { Timeline } from "./timeline";

type Sched = {
  id: string;
  text: string;
  color: string;
  t0: number;
  t1: number;
  anchor: (st: SceneState) => Vec3;
  dir: readonly [number, number];
  small?: boolean;
  dist?: number;
};

export const labelSchedule = (tl: Timeline): Sched[] => {
  const { ev, seg } = tl;
  const E = seg.engine.start;
  const G = seg.gearbox.start;
  const S = seg.support.start;
  const X = seg.explode.start;
  const fixed = (p: Vec3) => () => p;
  const list: Sched[] = [
    { id: "tank", text: "油箱", color: COLORS.fuelTank, t0: ev.tankHL, t1: E + 0.5, anchor: fixed([-0.8, 0.6, 0.3]), dir: [-0.5, -1] },
    { id: "fuelLine", text: "油管", color: COLORS.fuelLine, t0: ev.fuelFlow + 1.2, t1: E + 0.5, anchor: fixed([0.35, 0.3, 0.32]), dir: [0.2, 1], small: true, dist: 120 },
    { id: "engine", text: "发动机", color: COLORS.carOrange, t0: ev.engineHL, t1: G + 0.3, anchor: fixed([1.6, 0.7, 0.5]), dir: [-1, -0.5] },
    { id: "piston", text: "活塞", color: COLORS.rod, t0: ev.pistonHL, t1: G + 0.3, anchor: fixed([ENG.x + 0.05, 0.6, 0.12]), dir: [1, -0.2] },
    { id: "crank", text: "曲轴", color: COLORS.crank, t0: ev.crankHL, t1: G + 0.3, anchor: fixed([ENG.x + 0.04, ENG.crankY - 0.03, 0.03]), dir: [1, 0.6] },
    { id: "cam", text: "凸轮轴 · 气门", color: COLORS.cam, t0: ev.engineExtras, t1: G + 0.3, anchor: fixed([ENG.x + 0.055, 0.83, -0.03]), dir: [1, -0.5], small: true },
    { id: "plug", text: "火花塞", color: COLORS.plugCap, t0: ev.engineExtras + 0.4, t1: G + 0.3, anchor: fixed([ENG.x, 0.93, 0.28]), dir: [-0.6, -1], small: true },
    { id: "gearbox", text: "变速箱", color: COLORS.gearbox, t0: ev.gearboxHL, t1: S + 0.2, anchor: fixed([1.43, 0.555, -0.31]), dir: [-0.8, -1] },
    { id: "wheel", text: "车轮", color: COLORS.tire, t0: ev.wheelsShow + 0.6, t1: S + 0.2, anchor: fixed([1.32, 0.66, -0.88]), dir: [1, -0.6] },
    { id: "radiator", text: "散热器", color: COLORS.radiator, t0: ev.radiatorHL, t1: X + 0.3, anchor: fixed([1.98, 0.8, -0.35]), dir: [-0.3, -1] },
    { id: "oil", text: "机油", color: COLORS.oil, t0: ev.oilHL, t1: X + 0.3, anchor: fixed([1.58, 0.25, 0.35]), dir: [0.3, 1] },
    { id: "exhaust", text: "排气管", color: COLORS.exhaust, t0: ev.exhaustHL, t1: X + 0.3, anchor: fixed([-2.05, 0.22, -0.25]), dir: [-0.3, -1] },
  ];
  PART_IDS.forEach((id, k) => {
    list.push({
      id: `x_${id}`,
      text: PARTS[id].name,
      color: PARTS[id].color === COLORS.glass ? "#6E9BD1" : PARTS[id].color,
      t0: ev.labelsIn + k * 0.12,
      t1: ev.labelsOut + 0.35,
      anchor: (st) => labelAnchor(id, st.explode),
      dir: PARTS[id].labelDir,
      small: true,
      dist: 90,
    });
  });
  return list;
};

export const labelItems = (sched: readonly Sched[], st: SceneState): LabelItem[] =>
  sched
    .filter((s) => st.t >= s.t0 - 0.01 && st.t <= s.t1)
    .map((s) => ({
      id: s.id,
      text: s.text,
      color: s.color,
      anchor: s.anchor(st),
      dir: s.dir,
      small: s.small,
      dist: s.dist,
      pop: easeOutBack(ramp(st.t, s.t0, s.t0 + 0.35), 2),
      opacity: Math.min(smooth(ramp(st.t, s.t0, s.t0 + 0.12)), 1 - smooth(ramp(st.t, s.t1 - 0.3, s.t1))),
    }));

/** Points the cylinder-number tags hover over (just above each coil cap). */
export const cylinderTagAnchors = (): Vec3[] => ENG.cylZ.map((z) => [ENG.x, 0.99, z] as Vec3);
export const GEARBOX_INFO = GBX;
