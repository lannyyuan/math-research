/** When/where every Chinese label appears in the electric-car video (same style + rules as the gasoline car). */
import { easeOutBack, ramp, smooth } from "../lib/anim";
import type { Vec3 } from "../lib/camera";
import type { LabelItem } from "../components/LabelLayer";
import { COLORS } from "../style/theme";
import { CTRL, MOTOR, RED, TAIL_SPOT } from "./layout";
import { EV_PART_IDS, EV_PARTS } from "./parts";
import { evLabelAnchor, type EvSceneState } from "./state";
import type { EvTimeline } from "./timeline";

export type EvSched = {
  id: string;
  text: string;
  color: string;
  t0: number;
  t1: number;
  anchor: (st: EvSceneState) => Vec3;
  dir: readonly [number, number];
  small?: boolean;
  dist?: number;
};

export const evLabelSchedule = (tl: EvTimeline): EvSched[] => {
  const { ev, seg } = tl;
  const C = seg.controller.start;
  const M = seg.motor.start;
  const R = seg.reducer.start;
  const Q = seg.rear.start;
  const X = seg.explode.start;
  const fixed = (p: Vec3) => () => p;
  const list: EvSched[] = [
    { id: "battery", text: "电池包", color: COLORS.battery, t0: ev.batteryHL, t1: C + 0.5, anchor: fixed([-0.2, 0.4, 0.4]), dir: [-0.4, -1] },
    { id: "controller", text: "控制器", color: COLORS.controller, t0: ev.controllerHL, t1: M + 0.3, anchor: fixed([(CTRL.x0 + CTRL.x1) / 2, CTRL.y1, 0.12]), dir: [-0.2, -1] },
    { id: "harness", text: "高压线束", color: COLORS.hvCable, t0: ev.harnessLabel, t1: M + 0.3, anchor: fixed([1.07, 0.56, 0.2]), dir: [-1, 0.2], small: true },
    { id: "motor", text: "电机", color: COLORS.stator, t0: ev.motorHL, t1: R + 0.3, anchor: fixed([MOTOR.x - 0.02, MOTOR.y + MOTOR.r, 0.28]), dir: [0.3, -1] },
    { id: "stator", text: "定子", color: COLORS.coilA, t0: ev.statorRotor, t1: R + 0.3, anchor: fixed([MOTOR.x + 0.1, MOTOR.y - 0.03, MOTOR.z1 - 0.03]), dir: [1, 0.3], small: true },
    { id: "rotor", text: "转子", color: COLORS.magnetN, t0: ev.statorRotor + 0.35, t1: R + 0.3, anchor: fixed([MOTOR.x - 0.03, MOTOR.y - 0.02, MOTOR.z1 - 0.05]), dir: [-1, 0.5], small: true },
    { id: "reducer", text: "单速减速器", color: COLORS.reducer, t0: ev.reducerHL, t1: Q + 0.2, anchor: fixed([RED.diffX, RED.diffY + 0.13, RED.gearZ - 0.02]), dir: [-0.4, -1] },
    { id: "wheel", text: "车轮", color: COLORS.tire, t0: ev.wheelsShow + 0.6, t1: Q + 0.2, anchor: fixed([1.32, 0.66, -0.88]), dir: [1, -0.6] },
    { id: "noExhaust", text: "没有尾气", color: COLORS.leaf, t0: ev.noExhaust, t1: X + 0.3, anchor: fixed(TAIL_SPOT), dir: [-0.2, -1] },
  ];
  EV_PART_IDS.forEach((id, k) => {
    list.push({
      id: `x_${id}`,
      text: EV_PARTS[id].name,
      color: EV_PARTS[id].color,
      t0: ev.labelsIn + k * 0.12,
      t1: ev.labelsOut + 0.35,
      anchor: (st) => evLabelAnchor(id, st.explode),
      dir: EV_PARTS[id].labelDir,
      small: true,
      dist: 90,
    });
  });
  return list;
};

export const evLabelItems = (sched: readonly EvSched[], st: EvSceneState): LabelItem[] =>
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
