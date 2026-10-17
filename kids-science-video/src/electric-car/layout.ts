/**
 * Front-wheel-drive battery-electric sedan packaging (metres, same car axes
 * and body as the gasoline car — see three/car/carLayout.ts):
 *  - flat "skateboard" battery pack under the floor between the axles
 *  - transverse drive unit on the front axle: inverter (控制器) on top,
 *    permanent-magnet motor behind it, single-speed reducer on the car's left,
 *    differential on the axle line → half-shafts → front wheels
 *  - orange high-voltage cables: pack → inverter (DC) → motor (3 phases)
 */
import { CAR } from "../three/car/carLayout";

type V3 = readonly [number, number, number];

export const PACK = { x0: -0.84, x1: 0.82, y0: 0.255, y1: 0.395, z0: -0.66, z1: 0.66 } as const;
/** Cell modules: 2 rows across × 6 along the car, lit in this order (front → back, zig-zag). */
export const MODULES = (() => {
  const cols = 6;
  const rows = 2;
  const gap = 0.03;
  const w = (PACK.x1 - PACK.x0 - 0.08 - gap * (cols - 1)) / cols;
  const d = (PACK.z1 - PACK.z0 - 0.08 - gap * (rows - 1)) / rows;
  const out: { x: number; z: number; w: number; d: number; order: number }[] = [];
  for (let c = 0; c < cols; c++)
    for (let r = 0; r < rows; r++)
      out.push({
        x: PACK.x0 + 0.04 + w / 2 + c * (w + gap),
        z: PACK.z0 + 0.04 + d / 2 + r * (d + gap),
        w,
        d,
        order: c * rows + r,
      });
  return out;
})();

export const RED = {
  diffX: CAR.frontAxleX,
  diffY: CAR.wheelR,
  gearZ: -0.27,
  module: 0.005,
  nPinion: 11,
  nGear: 55,
  faceW: 0.034,
  housing: { x0: 1.16, x1: 1.6, y0: 0.205, y1: 0.63, z0: -0.4, z1: -0.145 },
} as const;
export const RATIO = RED.nGear / RED.nPinion; // 5 : 1

const centre = (RED.module * (RED.nPinion + RED.nGear)) / 2; // 0.165
const motorAngle = Math.atan2(0.123, 0.11);
/** Motor axis sits exactly one gear centre-distance from the differential. */
export const MOTOR = {
  x: RED.diffX + centre * Math.cos(motorAngle),
  y: RED.diffY + centre * Math.sin(motorAngle),
  r: 0.13,
  z0: -0.135,
  z1: 0.32,
  statorR: 0.112,
  rotorR: 0.066,
  slots: 12,
  polePairs: 2,
} as const;

export const CTRL = { x0: 1.27, x1: 1.63, y0: 0.645, y1: 0.8, z0: -0.3, z1: 0.3 } as const;

/** Length of the connector shell every HV cable ends in (it sits flush on its host's face). */
export const PLUG = 0.03;
/** Junction box on the pack's front face (cables leave it through connectors). */
export const JUNCTION = { x0: PACK.x1 + 0.01 - 0.04, x1: PACK.x1 + 0.01 + 0.04, y: 0.335, h: 0.035, z: 0.15, d: 0.08 } as const;

/** DC cables (+/−): pack junction box → along the floor → up the bulkhead → inverter's back face. */
export const DC_CABLES: readonly (readonly V3[])[] = [0.1, 0.2].map((z) => [
  [JUNCTION.x1 + PLUG, JUNCTION.y, z],
  [1.0, JUNCTION.y, z],
  [1.06, 0.4, z],
  [1.07, 0.72, z],
  [CTRL.x0 - PLUG, 0.72, z],
]);
/** Motor terminal box: sits on top of the motor housing, its front face at x1. */
export const TERMINAL = { x: MOTOR.x + 0.09, y: 0.59, x0: MOTOR.x + 0.06, x1: MOTOR.x + 0.12, y0: 0.57, y1: 0.61, z0: 0.03, z1: 0.25 } as const;
/** Three phase cables: inverter's front face → round the front → motor terminal box's front face. */
export const PHASE_CABLES: readonly (readonly V3[])[] = [0.06, 0.14, 0.22].map((z) => [
  [CTRL.x1 + PLUG, 0.7, z],
  [1.7, 0.7, z],
  [1.7, TERMINAL.y, z],
  [TERMINAL.x1 + PLUG, TERMINAL.y, z],
]);
/** Charge port on the right rear fender (where the gasoline car has its filler cap) → over the tyre → pack's rear face. */
export const CHARGE_CABLE: readonly V3[] = [
  [-1.53, 0.86, 0.78],
  [-1.5, 0.86, 0.58],
  [-1.0, 0.6, 0.5],
  [-0.95, 0.34, 0.45],
  [PACK.x0 - PLUG, 0.33, 0.45],
];
/** Connector shells: [from host face, to cable end], radius. */
export const PLUGS: readonly { a: V3; b: V3; r: number }[] = [
  ...[0.1, 0.2].flatMap((z) => [
    { a: [JUNCTION.x1, JUNCTION.y, z] as V3, b: [JUNCTION.x1 + PLUG, JUNCTION.y, z] as V3, r: 0.022 },
    { a: [CTRL.x0, 0.72, z] as V3, b: [CTRL.x0 - PLUG, 0.72, z] as V3, r: 0.022 },
  ]),
  ...[0.06, 0.14, 0.22].flatMap((z) => [
    { a: [CTRL.x1, 0.7, z] as V3, b: [CTRL.x1 + PLUG, 0.7, z] as V3, r: 0.019 },
    { a: [TERMINAL.x1, TERMINAL.y, z] as V3, b: [TERMINAL.x1 + PLUG, TERMINAL.y, z] as V3, r: 0.019 },
  ]),
  { a: [PACK.x0, 0.33, 0.45], b: [PACK.x0 - PLUG, 0.33, 0.45], r: 0.02 },
];
export const CHARGE_PORT: V3 = [-1.56, 0.865, 0.81];

/** Where the gasoline car's tailpipe exits — the EV shows clean air here instead. */
export const TAIL_SPOT: V3 = [-2.18, 0.26, -0.25];
