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

/** DC cables (+/−): pack front edge → along the floor → up the bulkhead → inverter. */
export const DC_CABLES: readonly (readonly V3[])[] = [0.1, 0.2].map((z) => [
  [PACK.x1 - 0.02, 0.33, z],
  [1.0, 0.33, z],
  [1.06, 0.4, z],
  [1.07, 0.72, z],
  [CTRL.x0 + 0.01, 0.72, z],
]);
/** Three phase cables: inverter front → motor terminal box. */
export const TERMINAL = { x: MOTOR.x + 0.098, y: MOTOR.y + 0.098 } as const;
export const PHASE_CABLES: readonly (readonly V3[])[] = [0.06, 0.14, 0.22].map((z) => [
  [CTRL.x1 - 0.05, CTRL.y0 + 0.005, z],
  [CTRL.x1 - 0.04, 0.62, z],
  [TERMINAL.x + 0.005, TERMINAL.y + 0.012, z],
]);
/** Charge port on the right rear fender (where the gasoline car has its filler cap) → pack. */
export const CHARGE_CABLE: readonly V3[] = [
  [-1.53, 0.86, 0.78],
  [-1.25, 0.6, 0.6],
  [-0.95, 0.34, 0.45],
  [PACK.x0 + 0.02, 0.33, 0.45],
];
export const CHARGE_PORT: V3 = [-1.56, 0.865, 0.81];

/** Where the gasoline car's tailpipe exits — the EV shows clean air here instead. */
export const TAIL_SPOT: V3 = [-2.18, 0.26, -0.25];
