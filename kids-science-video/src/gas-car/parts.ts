/**
 * Registry of every labelled part: Chinese name, label anchor (assembled
 * position) and exploded-view offset. The explode offsets are hand-tuned for
 * a readable "parts cloud", and scripts/check-scene.ts verifies each one
 * points away from the car centre.
 */
import { COLORS } from "../style/theme";
import { CAR } from "../three/car/carLayout";

type V3 = readonly [number, number, number];

export const PART_IDS = [
  "fuelTank",
  "fuelLine",
  "block",
  "pistons",
  "crankshaft",
  "camValves",
  "sparkPlugs",
  "intake",
  "exhaustManifold",
  "exhaustPipe",
  "gearbox",
  "halfShafts",
  "radiator",
  "oil",
  "wheels",
] as const;
export type PartId = (typeof PART_IDS)[number];

export type PartDef = {
  readonly name: string;
  readonly color: string;
  /** Where the label's leader line points (assembled position, metres). */
  readonly anchor: V3;
  /** Offset at full explosion (metres). */
  readonly explode: V3;
  /** Preferred label direction on screen (x right, y down). */
  readonly labelDir: readonly [number, number];
};

export const PARTS: Record<PartId, PartDef> = {
  fuelTank: { name: "油箱", color: COLORS.fuelTank, anchor: [-0.8, 0.5, 0.3], explode: [-1.15, 0.3, 0.75], labelDir: [-1, 0.6] },
  fuelLine: { name: "油管", color: COLORS.fuelLine, anchor: [0.35, 0.3, 0.32], explode: [0.54, -0.04, 1.62], labelDir: [0, 1] },
  block: { name: "发动机缸体", color: COLORS.glass, anchor: [1.48, 0.5, 0.4], explode: [0.84, 0.48, -0.53], labelDir: [1, 0.15] },
  pistons: { name: "活塞和连杆", color: COLORS.piston, anchor: [1.48, 0.6, 0.36], explode: [0.41, 1.16, -0.55], labelDir: [1, -0.1] },
  crankshaft: { name: "曲轴", color: COLORS.crank, anchor: [1.48, 0.4, 0.36], explode: [0.82, -0.04, 0.56], labelDir: [1, 0.6] },
  camValves: { name: "凸轮轴和气门", color: COLORS.cam, anchor: [1.48, 0.815, 0.3], explode: [1.14, 1.36, -0.94], labelDir: [1, -0.3] },
  sparkPlugs: { name: "火花塞", color: COLORS.plugCap, anchor: [1.48, 0.92, 0.3], explode: [0.15, 1.62, -0.57], labelDir: [0.3, -1] },
  intake: { name: "进气歧管", color: COLORS.intake, anchor: [1.19, 0.8, 0.2], explode: [0.06, 1.01, -0.35], labelDir: [-0.4, -1] },
  exhaustManifold: { name: "排气歧管", color: COLORS.exhaust, anchor: [1.7, 0.6, 0.25], explode: [1.56, -0.08, 0.02], labelDir: [1, 0.2] },
  exhaustPipe: { name: "排气管", color: COLORS.exhaust, anchor: [-1.75, 0.2, -0.25], explode: [-0.6, 0.0, -0.9], labelDir: [-1, 0.5] },
  gearbox: { name: "变速箱", color: COLORS.gearbox, anchor: [1.43, 0.4, -0.31], explode: [2.38, 1.22, -1.46], labelDir: [0.3, -1] },
  halfShafts: { name: "半轴", color: COLORS.shaft, anchor: [1.32, 0.36, 0.45], explode: [0.14, 0.0, 0.56], labelDir: [0.2, 1] },
  radiator: { name: "散热器", color: COLORS.radiator, anchor: [1.98, 0.6, 0.0], explode: [1.81, 0.04, -0.83], labelDir: [1, -0.4] },
  oil: { name: "机油", color: COLORS.oil, anchor: [1.48, 0.26, 0.3], explode: [1.54, 0.0, 1.42], labelDir: [1, 0.8] },
  wheels: { name: "车轮", color: COLORS.tire, anchor: [CAR.frontAxleX, CAR.wheelR, CAR.trackHalf + 0.12], explode: [0.0, 0.0, 0.0], labelDir: [-0.3, 1] },
};

/** Wheels explode individually (outwards along the axles). */
export const WHEEL_EXPLODE: Record<string, V3> = {
  FL: [0.25, 0, -0.75],
  FR: [0.25, 0, 0.75],
  RL: [-0.25, 0, -0.75],
  RR: [-0.25, 0, 0.75],
};
