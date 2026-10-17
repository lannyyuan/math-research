/**
 * The true shape of every EV part, as drawn (same numbers as three/Drive.tsx),
 * grouped by explode assembly — input to the geometric audit (lib/sdfAudit.ts).
 */
import type { Mount, Shape } from "../lib/sdfAudit";
import { roundedPath } from "../three/geometry";
import { CAR, WHEELS } from "../three/car/carLayout";
import { CHARGE_CABLE, CTRL, DC_CABLES, JUNCTION, MOTOR, PACK, PHASE_CABLES, PLUGS, RED, TERMINAL } from "./layout";

type V3 = readonly [number, number, number];

const cableShapes = (name: string, group: string, pts: readonly V3[], r: number, corner: number): Shape[] => {
  const path = roundedPath(pts, corner);
  const n = Math.max(8, Math.ceil(path.getLength() / 0.03));
  const s = path.getSpacedPoints(n).map((p) => [p.x, p.y, p.z] as V3);
  return s.slice(1).map((b, i) => ({ kind: "capsule" as const, name: `${name}#${i}`, group, a: s[i], b, r }));
};
const cylZ = (name: string, group: string, x: number, y: number, z0: number, z1: number, r: number): Shape => ({
  kind: "cyl",
  name,
  group,
  a: [x, y, z0],
  b: [x, y, z1],
  r,
});
const box = (name: string, group: string, min: V3, max: V3): Shape => ({
  kind: "box",
  name,
  group,
  c: [(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2],
  h: [(max[0] - min[0]) / 2, (max[1] - min[1]) / 2, (max[2] - min[2]) / 2],
});

/** Electrical connectors at cable ends (drawn by Drive.tsx too): [name, from, to, radius]. */
export const evConnectors = (): { name: string; a: V3; b: V3; r: number }[] => PLUGS.map((p, i) => ({ name: `harness.plug${i}`, ...p }));

export const evShapes = (): Shape[] => {
  const s: Shape[] = [];
  // battery pack + junction box
  s.push(box("battery.pack", "battery", [PACK.x0, PACK.y0, PACK.z0], [PACK.x1, PACK.y1, PACK.z1]));
  s.push(box("battery.junction", "battery", [JUNCTION.x0, JUNCTION.y - JUNCTION.h, JUNCTION.z - JUNCTION.d], [JUNCTION.x1, JUNCTION.y + JUNCTION.h, JUNCTION.z + JUNCTION.d]));
  // harness
  DC_CABLES.forEach((p, i) => s.push(...cableShapes(`harness.dc${i}`, "harness", p, 0.013, 0.05)));
  PHASE_CABLES.forEach((p, i) => s.push(...cableShapes(`harness.ac${i}`, "harness", p, 0.011, 0.04)));
  s.push(...cableShapes("harness.charge", "harness", CHARGE_CABLE, 0.012, 0.08));
  for (const c of evConnectors()) s.push({ kind: "cyl", name: c.name, group: "harness", a: c.a, b: c.b, r: c.r });
  // controller
  s.push(box("controller.box", "controller", [CTRL.x0, CTRL.y0, CTRL.z0], [CTRL.x1, CTRL.y1 + 0.012, CTRL.z1]));
  // motor: housing, shaft (through the pinion into the reducer), terminal box
  s.push(cylZ("motor.housing", "motor", MOTOR.x, MOTOR.y, MOTOR.z0, MOTOR.z1, MOTOR.r));
  s.push(cylZ("motor.shaft", "motor", MOTOR.x, MOTOR.y, RED.gearZ - 0.03, MOTOR.z1 + 0.05, 0.016));
  s.push(box("motor.terminalBox", "motor", [TERMINAL.x0, TERMINAL.y0, TERMINAL.z0], [TERMINAL.x1, TERMINAL.y1, TERMINAL.z1]));
  // reducer
  const h = RED.housing;
  s.push(box("reducer.housing", "reducer", [h.x0, h.y0, h.z0], [h.x1, h.y1, h.z1]));
  // half-shafts with their CV boots
  const zL0 = RED.gearZ - 0.045;
  const zL1 = -(CAR.trackHalf - 0.1);
  const zR0 = RED.gearZ + 0.03;
  const zR1 = CAR.trackHalf - 0.1;
  s.push(cylZ("halfShafts.left", "halfShaftL", RED.diffX, RED.diffY, zL1, zL0, 0.017));
  s.push(cylZ("halfShafts.right", "halfShaftR", RED.diffX, RED.diffY, zR0, zR1, 0.017));
  for (const [nm, z, grp] of [
    ["halfShafts.bootLo", zL1 + 0.04, "halfShaftL"],
    ["halfShafts.bootLi", zL0 - 0.03, "halfShaftL"],
    ["halfShafts.bootRi", zR0 + 0.04, "halfShaftR"],
    ["halfShafts.bootRo", zR1 - 0.04, "halfShaftR"],
  ] as const)
    s.push(cylZ(nm, grp, RED.diffX, RED.diffY, z - 0.035, z + 0.035, 0.035));
  // wheels (tyre envelope)
  for (const w of WHEELS) s.push(cylZ(`wheel${w.id}.tyre`, `wheel${w.id}`, w.x, CAR.wheelR, w.z - 0.095, w.z + 0.095, CAR.wheelR));
  // static chassis
  s.push(cylZ("static.rearBeam", "static", CAR.rearAxleX, CAR.wheelR - 0.02, -(CAR.trackHalf - 0.1), CAR.trackHalf - 0.1, 0.03));
  return s.filter((x) => !(x.kind === "sphere" && x.r < 0.01));
};

/** Joints that touch by design. `axis` = the direction they come apart along (a slide). */
export const EV_MOUNTS: Mount[] = [
  { a: "motor.shaft", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "motor.housing", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "halfShafts.left", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "halfShafts.right", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "halfShafts.bootLi", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "halfShafts.bootRi", b: "reducer.housing", axis: [0, 0, 1] },
  { a: "halfShafts.bootLo", b: "wheelFL.tyre", axis: [0, 0, 1] },
  { a: "halfShafts.bootRo", b: "wheelFR.tyre", axis: [0, 0, 1] },
];

/** Cable ends and what they must land on at rest. */
/** Cable ends (both ends of every HV cable) — each must end on a connector shell. */
export const evCableEnds = (): V3[] => [
  ...DC_CABLES.flatMap((c) => [c[0], c[c.length - 1]]),
  ...PHASE_CABLES.flatMap((c) => [c[0], c[c.length - 1]]),
  CHARGE_CABLE[CHARGE_CABLE.length - 1],
];
