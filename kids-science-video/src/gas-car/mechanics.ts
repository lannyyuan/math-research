/**
 * Engine + drivetrain kinematics. Everything is precomputed per frame by
 * integrating angular speeds over the timeline, so state at frame N depends
 * only on N (no wall clock) and the visuals, labels and engine sound all read
 * the same numbers.
 *
 * Conventions (all angles in radians):
 *  - θ  = crank angle. Crank pin of cylinder i is at angle θ + PHASE[i] measured
 *         from +Y towards +X; cylinder 1 is at compression TDC when θ ≡ 0 (mod 4π).
 *  - camshafts turn at exactly θ/2 (timing belt 1:2).
 *  - w  = road-wheel angle (forward roll). Wheel/half-shaft rotation.z = −w.
 */
import { CAR } from "../three/car/carLayout";
import { camProfile } from "../three/geometry";
import { wrapPi, smooth, ramp, lerp } from "../lib/anim";
import { ENG, GBX, RATIOS } from "./layout";
import type { Timeline } from "./timeline";

const PI = Math.PI;

/** Crank-pin phase per cylinder (1 & 4 together, 2 & 3 opposite). */
export const PIN_PHASE = [0, PI, PI, 0] as const;
/** Crank angle (mod 4π) at which each cylinder fires → order 1-3-4-2. */
export const FIRE_AT = [0, 3 * PI, PI, 2 * PI] as const;
export const FIRING_ORDER = [1, 3, 4, 2] as const;

export const crankPin = (theta: number, i: number) => {
  const a = theta + PIN_PHASE[i];
  return { x: ENG.x + ENG.throw * Math.sin(a), y: ENG.crankY + ENG.throw * Math.cos(a) };
};

/** Piston (wrist-pin) height from the slider-crank relation. */
export const pistonPinY = (theta: number, i: number) => {
  const a = theta + PIN_PHASE[i];
  const r = ENG.throw;
  const s = r * Math.sin(a);
  return ENG.crankY + r * Math.cos(a) + Math.sqrt(ENG.rod * ENG.rod - s * s);
};

const mod = (a: number, m: number) => ((a % m) + m) % m;

/** Crank angle elapsed since cylinder i last fired, in [0, 4π). */
export const sinceFire = (theta: number, i: number) => mod(theta - FIRE_AT[i], 4 * PI);

/** Spark/combustion flash 0..1 — only right after this cylinder's own firing point. */
export const sparkFlash = (theta: number, i: number, omegaE: number) => {
  const p = sinceFire(theta, i);
  const window = 0.9;
  const running = smooth(omegaE / 0.25);
  if (p < window) return Math.pow(1 - p / window, 1.4) * running;
  // the plug sparks a hair before TDC
  if (p > 4 * PI - 0.12) return 0.6 * running;
  return 0;
};

export const CAM_HALF_WIDTH = PI / 3; // ±60° of cam = ±120° of crank

/** Valve lift in metres, from the actual cam-lobe angle (cam = θ/2). */
export const valveLift = (theta: number, i: number, kind: "intake" | "exhaust") => {
  const peak = FIRE_AT[i] + (kind === "intake" ? 2.5 * PI : 1.5 * PI);
  const delta = wrapPi((theta - peak) / 2);
  return camProfile(delta, ENG.camBaseR, ENG.camLift, CAM_HALF_WIDTH) - ENG.camBaseR;
};

/** Local lobe angle (from +Y towards +X) so that the lobe faces its valve at peak lift. */
export const lobeAngle = (i: number, kind: "intake" | "exhaust", valveDirAngle: number) => {
  const peak = FIRE_AT[i] + (kind === "intake" ? 2.5 * PI : 1.5 * PI);
  return valveDirAngle - peak / 2;
};

export type DriveState = {
  theta: number;
  omegaE: number; // crank rev/s
  wheel: number; // road-wheel angle
  omegaW: number; // wheel rev/s
  dist: number; // metres travelled (for road scroll)
  gear: number; // 0 = neutral, 1..3
  gearFrom: number;
  shiftU: number; // 0..1 progress of the current shift
};

const IDLE = 0.8;
const SLOW_MO = 0.55;
const CRUISE_W = 0.5;

const smax = (a: number, b: number, k = 0.08) => (a + b + Math.sqrt((a - b) * (a - b) + k * k)) / 2;

export const buildDrive = (tl: Timeline) => {
  const { ev, seg, fps } = tl;
  const n = tl.totalFrames + 1;
  const R = RATIOS.gear.map((g) => g * RATIOS.final);

  const wheelSpeed = (t: number) => {
    if (t < ev.driveStart) return 0;
    if (t < ev.stop[0]) return CRUISE_W * smooth(ramp(t, ev.driveStart, ev.cruiseReached));
    if (t < ev.driveAway) return CRUISE_W * (1 - smooth(ramp(t, ev.stop[0], ev.stop[1])));
    return 0.2 * smooth(ramp(t, ev.driveAway, ev.driveAway + 1.6));
  };
  const shifts = [
    { t: ev.driveStart - 0.4, from: 0, to: 1 },
    { t: ev.shift1, from: 1, to: 2 },
    { t: ev.shift2, from: 2, to: 3 },
    { t: ev.stop[0] - 0.05, from: 3, to: 0 }, // clutch in / neutral while braking
    { t: ev.driveAway - 0.45, from: 0, to: 1 },
  ];
  const gearState = (t: number) => {
    let gear = 0;
    let from = 0;
    let u = 1;
    for (const s of shifts) {
      if (t >= s.t) {
        gear = s.to;
        from = s.from;
        u = ramp(t, s.t, s.t + ev.shiftDur);
      }
    }
    return { gear, from, u };
  };
  const engineSpeed = (t: number, w: number) => {
    const { gear, from, u } = gearState(t);
    // engine on/off
    if (t >= ev.stop[0] && t < ev.restart) return IDLE * (1 - smooth(ramp(t, ev.stop[0] + 0.2, ev.stop[1] + 0.1)));
    const restartK = t >= ev.restart ? smooth(ramp(t, ev.restart, ev.restart + 0.6)) : 1;
    // the engine close-up runs in slow motion so pistons are easy to follow
    let idle = IDLE;
    if (t >= ev.engineSlowMo[0] && t < seg.gearbox.start + 1.2) {
      const kIn = smooth(ramp(t, ev.engineSlowMo[0], ev.engineSlowMo[1]));
      const kOut = smooth(ramp(t, seg.gearbox.start, seg.gearbox.start + 1.2));
      idle = lerp(IDLE, lerp(SLOW_MO, IDLE, kOut), kIn);
    }
    const coupled = (g: number) => (g === 0 ? idle : smax(idle, R[g - 1] * w));
    const e = u < 1 ? lerp(coupled(from), coupled(gear), smooth(u)) : coupled(gear);
    return e * restartK;
  };

  const theta = new Float64Array(n);
  const omegaE = new Float64Array(n);
  const wheel = new Float64Array(n);
  const omegaW = new Float64Array(n);
  const dist = new Float64Array(n);
  for (let f = 1; f < n; f++) {
    const tMid = (f - 0.5) / fps;
    const w = wheelSpeed(tMid);
    const e = engineSpeed(tMid, w);
    omegaW[f] = wheelSpeed(f / fps);
    omegaE[f] = engineSpeed(f / fps, omegaW[f]);
    theta[f] = theta[f - 1] + (2 * PI * e) / fps;
    wheel[f] = wheel[f - 1] + (2 * PI * w) / fps;
    dist[f] = wheel[f] * CAR.wheelR;
  }
  omegaE[0] = engineSpeed(0, 0);

  // Phase-align so a cylinder fires exactly on the "砰" in the narration.
  const fp = ev.peng * fps;
  const f0 = Math.floor(fp);
  const thetaAtPeng = lerp(theta[f0], theta[f0 + 1], fp - f0);
  const shift = -mod(thetaAtPeng, PI);
  for (let f = 0; f < n; f++) theta[f] += shift;

  const at = (frame: number): DriveState => {
    const f = Math.max(0, Math.min(n - 1, Math.round(frame)));
    const t = f / fps;
    const g = gearState(t);
    return {
      theta: theta[f],
      omegaE: omegaE[f],
      wheel: wheel[f],
      omegaW: omegaW[f],
      dist: dist[f],
      gear: g.gear,
      gearFrom: g.from,
      shiftU: g.u,
    };
  };

  /** Every firing event (time, cylinder number) — drives the engine sound and the 1-3-4-2 panel. */
  const firings: { t: number; cyl: number }[] = [];
  for (let f = 1; f < n; f++) {
    for (let i = 0; i < 4; i++) {
      const a = Math.floor((theta[f - 1] - FIRE_AT[i]) / (4 * PI));
      const b = Math.floor((theta[f] - FIRE_AT[i]) / (4 * PI));
      if (b > a) {
        const target = FIRE_AT[i] + b * 4 * PI;
        const u = (target - theta[f - 1]) / (theta[f] - theta[f - 1]);
        firings.push({ t: (f - 1 + u) / fps, cyl: i + 1 });
      }
    }
  }
  firings.sort((p, q) => p.t - q.t);

  return { at, theta, omegaE, wheel, omegaW, firings, gearState, ratios: R };
};

export type Drive = ReturnType<typeof buildDrive>;

/** Constant phase for a gear B meshing with gear A along centre-line angle λ (math angle). */
export const meshPhase = (lambda: number, nA: number, nB: number) => {
  const stepB = (2 * PI) / nB;
  const rhoA0 = lambda - PI / 2;
  const rhoB0 = lambda + PI / 2 + stepB / 2;
  return rhoB0 + (rhoA0 * nA) / nB;
};

export const GEAR_INFO = GBX;
