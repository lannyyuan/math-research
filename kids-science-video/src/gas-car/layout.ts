/**
 * Where every powertrain part sits in the gasoline car (metres, car axes —
 * see three/car/carLayout.ts). Real transverse inline-4 front-wheel-drive
 * packaging: engine across the bay, gearbox (transaxle) on the car's left,
 * half-shafts on the front axle line, tank under the rear seat, exhaust
 * along the floor to the rear.
 */
import { CAR } from "../three/car/carLayout";

type V3 = readonly [number, number, number];

export const ENG = {
  x: 1.48,
  crankY: 0.4,
  throw: 0.05,
  rod: 0.16,
  /** Cylinder 1 is at the timing-belt end (+Z), as on real engines. */
  cylZ: [0.44, 0.28, 0.12, -0.04] as const,
  boreR: 0.062,
  pistonH: 0.075,
  pinToCrown: 0.035,
  deckY: 0.66,
  chamberTopY: 0.676,
  headTopY: 0.77,
  coverTopY: 0.88,
  blockHalfX: 0.11,
  headHalfX: 0.12,
  blockZ0: -0.12,
  blockZ1: 0.52,
  crankcaseY0: 0.31,
  panY0: 0.22,
  camY: 0.815,
  camDX: 0.055,
  camBaseR: 0.02,
  camLift: 0.014,
  /** Valve-head centres sit ±valveDX from the bore axis. */
  valveDX: 0.03,
  valveHeadR: 0.021,
  beltZ: 0.566,
  crankSprocketR: 0.035,
  camSprocketR: 0.07,
  flywheelZ: -0.135,
} as const;

/** Gearbox / transaxle on the car's left (−Z) end of the engine. */
export const GBX = {
  inX: ENG.x,
  inY: ENG.crankY,
  diffX: CAR.frontAxleX,
  diffY: CAR.wheelR,
  diffZ: -0.405,
  module: 0.006,
  finalModule: 0.004,
  /** Teeth: [input, output] for 1st/2nd/3rd — all pairs share the same centre distance. */
  gears: [
    { name: "1档", nIn: 10, nOut: 25, z: -0.19 },
    { name: "2档", nIn: 14, nOut: 21, z: -0.27 },
    { name: "3档", nIn: 17, nOut: 18, z: -0.33 },
  ] as const,
  final: { nPinion: 6, nRing: 24 },
  faceW: 0.03,
  housing: { x0: 1.24, x1: 1.63, y0: 0.255, y1: 0.555, z0: -0.5, z1: -0.128 },
} as const;

const centreDist = (GBX.module * (GBX.gears[0].nIn + GBX.gears[0].nOut)) / 2; // 0.105
const finalDist = (GBX.finalModule * (GBX.final.nPinion + GBX.final.nRing)) / 2; // 0.06
const dx = GBX.diffX - GBX.inX;
const dy = GBX.diffY - GBX.inY;
const d = Math.hypot(dx, dy);
/** Output (lay) shaft lies on the input→differential line so both meshes have exact centre distances. */
export const OUT_SHAFT = { x: GBX.inX + (dx / d) * centreDist, y: GBX.inY + (dy / d) * centreDist };
export const GEAR_GEOM_CHECK = { centreDist, finalDist, inputToDiff: d };

export const RATIOS = {
  gear: GBX.gears.map((g) => g.nOut / g.nIn),
  final: GBX.final.nRing / GBX.final.nPinion,
};

export const TANK = { x0: -1.16, x1: -0.44, y0: 0.32, y1: 0.6, z0: -0.46, z1: 0.46 } as const;

/** Fuel: tank → floor → up the firewall → over the intake plenum → fuel rail. */
export const FUEL_LINE: readonly V3[] = [
  [-0.44, 0.4, 0.32],
  [-0.3, 0.3, 0.32],
  [0.94, 0.3, 0.32],
  [1.02, 0.36, 0.42],
  [1.02, 0.88, 0.46],
  [1.31, 0.88, 0.46],
  [1.31, 0.835, 0.46],
];
export const FUEL_RAIL = { x: 1.31, y: 0.822, z0: -0.07, z1: 0.5, r: 0.012 } as const;

export const INTAKE = { plenumX: 1.19, plenumY: 0.79, plenumR: 0.05, z0: -0.08, z1: 0.5 } as const;
export const AIR_PIPE: readonly V3[] = [
  [1.19, 0.79, -0.08],
  [1.19, 0.8, -0.24],
  [1.24, 0.9, -0.26],
  [1.7, 0.89, -0.26],
];

export const EXHAUST_COLLECTOR: V3 = [1.745, 0.52, 0.2];
export const EXHAUST_PIPE: readonly V3[] = [
  [1.745, 0.5, 0.19],
  [1.755, 0.3, 0.1],
  [1.7, 0.17, 0.0],
  [1.2, 0.17, -0.03],
  [0.2, 0.17, -0.08],
  [-1.5, 0.17, -0.2],
  [-1.62, 0.2, -0.25],
];
export const MUFFLER = { x0: -1.98, x1: -1.56, y: 0.21, r: 0.075, z: -0.25 } as const;
export const TAILPIPE: readonly V3[] = [
  [-1.97, 0.2, -0.25],
  [-2.25, 0.2, -0.25],
];
export const CATALYST = { x0: 0.35, x1: 0.8, y: 0.17, r: 0.055, z: -0.065 } as const;

export const RADIATOR = { x: 1.98, thick: 0.05, y0: 0.34, y1: 0.8, z0: -0.62, z1: 0.62 } as const;
export const FAN = { x: 1.89, y: 0.57, z: 0.15, r: 0.18 } as const;
export const UPPER_HOSE: readonly V3[] = [
  [1.955, 0.76, 0.42],
  [1.8, 0.75, 0.47],
  [1.625, 0.74, 0.5],
];
export const LOWER_HOSE: readonly V3[] = [
  [1.955, 0.4, -0.42],
  [1.75, 0.41, -0.3],
  [1.592, 0.42, -0.08],
];

/** Oil circulation (pan → pump → main gallery → crank → head → cams → drains back). */
export const OIL_PATH: readonly V3[] = [
  [1.52, 0.245, 0.3],
  [1.56, 0.33, 0.48],
  [1.56, 0.4, 0.48],
  [1.56, 0.4, -0.1],
  [1.48, 0.4, -0.08],
  [1.48, 0.4, 0.5],
  [1.575, 0.5, 0.5],
  [1.575, 0.8, 0.5],
  [1.535, 0.815, 0.5],
  [1.535, 0.815, -0.1],
  [1.425, 0.815, -0.1],
  [1.425, 0.815, 0.5],
  [1.385, 0.6, 0.5],
  [1.4, 0.26, 0.4],
];
