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
  battery: { name: "电池包", color: COLORS.battery, anchor: [(PACK.x0 + PACK.x1) / 2 - 0.2, PACK.y1, 0.3], explode: [0.69, -0.04, 1.84], labelDir: [-1, 0.6] },
  harness: { name: "高压线束", color: COLORS.hvCable, anchor: [1.0, 0.33, 0.15], explode: [0.41, 0.89, 0.76], labelDir: [-0.4, -1] },
  controller: { name: "控制器", color: COLORS.controller, anchor: [(CTRL.x0 + CTRL.x1) / 2, CTRL.y1, 0.1], explode: [1.29, 1.21, 1.41], labelDir: [-0.3, -1] },
  motor: { name: "电机", color: COLORS.stator, anchor: [MOTOR.x, MOTOR.y + MOTOR.r, 0.1], explode: [2.13, 0.74, 1.59], labelDir: [1, -0.3] },
  reducer: { name: "单速减速器", color: COLORS.reducer, anchor: [1.38, 0.5, -0.27], explode: [2.44, 1.35, 0.15], labelDir: [1, -0.6] },
  halfShafts: { name: "半轴", color: COLORS.shaft, anchor: [RED.diffX, RED.diffY, 0.45], explode: [0.66, -0.2, 0.56], labelDir: [0.2, 1] },
  wheels: { name: "车轮", color: COLORS.tire, anchor: [CAR.frontAxleX, CAR.wheelR, CAR.trackHalf + 0.12], explode: [0, 0, 0], labelDir: [-0.3, 1] },
};

/** Same wheel explode as the gasoline car → identical motion rules side by side. */
export const EV_WHEEL_EXPLODE: Record<string, V3> = {
  FL: [0.25, 0, -0.75],
  FR: [0.25, 0, 0.75],
  RL: [-0.25, 0, -0.75],
  RR: [-0.25, 0, 0.75],
};
