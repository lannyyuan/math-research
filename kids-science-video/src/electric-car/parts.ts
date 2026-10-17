/**
 * Labelled EV parts: Chinese name, anchor and exploded-view offset.
 * Same explode rules and label style as the gasoline car; only a few big blocks.
 */
import { COLORS } from "../style/theme";
import { CAR } from "../three/car/carLayout";
import { CTRL, MOTOR, PACK, RED } from "./layout";

type V3 = readonly [number, number, number];

export const EV_PART_IDS = ["battery", "harness", "controller", "motor", "reducer", "halfShafts", "wheels"] as const;
export type EvPartId = (typeof EV_PART_IDS)[number];

export type EvPartDef = {
  readonly name: string;
  readonly color: string;
  readonly anchor: V3;
  readonly explode: V3;
  readonly labelDir: readonly [number, number];
};

export const EV_PARTS: Record<EvPartId, EvPartDef> = {
  battery: { name: "电池包", color: COLORS.battery, anchor: [(PACK.x0 + PACK.x1) / 2 - 0.2, PACK.y1, 0.3], explode: [0.2, -0.04, 1.84], labelDir: [-1, 0.6] },
  harness: { name: "高压线束", color: COLORS.hvCable, anchor: [1.07, 0.72, 0.15], explode: [0.41, 0.89, 0.76], labelDir: [-0.4, -1] },
  controller: { name: "控制器", color: COLORS.controller, anchor: [(CTRL.x0 + CTRL.x1) / 2, CTRL.y1, 0.1], explode: [1.29, 1.21, 1.41], labelDir: [-0.3, -1] },
  motor: { name: "电机", color: COLORS.stator, anchor: [MOTOR.x, MOTOR.y + MOTOR.r, 0.1], explode: [2.13, 0.74, 1.59], labelDir: [1, -0.3] },
  reducer: { name: "单速减速器", color: COLORS.reducer, anchor: [1.38, 0.5, -0.27], explode: [2.44, 1.35, 0.15], labelDir: [1, -0.6] },
  halfShafts: { name: "半轴", color: COLORS.shaft, anchor: [RED.diffX, RED.diffY, 0.45], explode: [0.66, -0.2, 0.56], labelDir: [0.2, 1] },
  wheels: { name: "车轮", color: COLORS.tire, anchor: [CAR.frontAxleX, CAR.wheelR, CAR.trackHalf + 0.12], explode: [0, 0, 0], labelDir: [-0.3, 1] },
};

/** Same wheel explode targets as the gasoline car → identical layout side by side. */
export const EV_WHEEL_EXPLODE: Record<string, V3> = {
  FL: [0.25, 0, -0.75],
  FR: [0.25, 0, 0.75],
  RL: [-0.25, 0, -0.75],
  RR: [-0.25, 0, 0.75],
};

/**
 * Teardown choreography (method from the "anatomy" skill): assemblies leave one after
 * another in the order a mechanic would take them off, each first sliding out along its
 * real disassembly axis (`EV_EXIT`) until it is clear of its neighbours, then gliding to
 * its spot in the parts cloud. The merge runs the same paths backwards in reverse order
 * (last out, first back). scripts/audit-ev.ts proves nothing passes through anything.
 */
export const EV_EXPLODE_ORDER = ["wheels", "controller", "harness", "motor", "halfShafts", "reducer", "battery"] as const;
/** Departure time of each assembly (s after the teardown starts), in EV_EXPLODE_ORDER. */
export const EV_DEPART = [0, 0.15, 0.3, 0.45, 0.6, 1.0, 1.15] as const; // the reducer waits until both half-shafts are out
export const EV_LEG_TIME = 1.15; // s each assembly takes
export const EV_TEARDOWN = EV_DEPART[EV_DEPART.length - 1] + EV_LEG_TIME;
export const EV_EXIT: Partial<Record<EvPartId, V3>> = {
  controller: [0, 0.3, 0], // lift straight off the drive unit
  harness: [0, 0.3, 0.25], // every plug slides off parallel to the face it sits on
  motor: [0, 0, 0.35], // pull the shaft out of the pinion along its own axis
  reducer: [0.2, 0.3, -0.1], // shafts already out: lift it off forwards
};
/**
 * The two half-shafts are pulled out of the differential along the axle, each to its own side,
 * then slide away outwards on that side (the right one carries the label).
 */
export const EV_HALF_SHAFTS = {
  right: { exit: [0, 0, 0.4] as V3, final: [0.66, -0.2, 0.56] as V3 },
  left: { exit: [0, 0, -0.4] as V3, final: [0.6, -0.2, -0.45] as V3 },
};
/** Wheels slide off their hubs along the axle before swinging out. */
export const EV_WHEEL_EXIT: Record<string, V3> = {
  FL: [0, 0, -0.3],
  FR: [0, 0, 0.3],
  RL: [0, 0, -0.3],
  RR: [0, 0, 0.3],
};

/** Position along an exit-then-glide path at progress s ∈ [0, 1] (constant speed along the path). */
export const pathOffset = (exit: V3 | undefined, final: V3, s: number): V3 => {
  if (!exit) return [final[0] * s, final[1] * s, final[2] * s];
  const l1 = Math.hypot(...exit);
  const leg2: V3 = [final[0] - exit[0], final[1] - exit[1], final[2] - exit[2]];
  const l2 = Math.hypot(...leg2);
  const u = s * (l1 + l2);
  if (u <= l1) return [exit[0] * (u / l1), exit[1] * (u / l1), exit[2] * (u / l1)];
  const k = (u - l1) / l2;
  return [exit[0] + leg2[0] * k, exit[1] + leg2[1] * k, exit[2] + leg2[2] * k];
};
