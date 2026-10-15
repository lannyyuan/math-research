/**
 * Electric drive kinematics, precomputed per frame (frame number → state):
 *  - road-wheel angle w is integrated from the wheel-speed profile
 *  - the reducer is one gear pair: rotor/pinion turns RATIO× faster and in the
 *    opposite sense to the big gear (rotation.z: gear = −w, pinion = +RATIO·w)
 *  - a permanent-magnet motor: the stator's rotating field is locked to the
 *    rotor (electrical angle = pole pairs × rotor angle)
 *  - power always flows battery → controller → motor
 */
import { CAR } from "../three/car/carLayout";
import { lerp, ramp, smooth } from "../lib/anim";
import { MOTOR, RATIO } from "./layout";
import type { EvTimeline } from "./timeline";

const PI = Math.PI;
const CRUISE_W = 0.5;

export type EvDriveState = {
  wheel: number;
  omegaW: number;
  rotor: number; // rotor angle (rad), = RATIO · wheel
  omegaR: number; // rotor rev/s
  dist: number;
  power: number; // 0..1 how hard the motor is being fed
};

export const buildEvDrive = (tl: EvTimeline) => {
  const { ev, fps } = tl;
  const n = tl.totalFrames + 1;
  const wheelSpeed = (t: number) => {
    if (t < ev.driveStart) return 0;
    if (t < ev.stop[0]) return CRUISE_W * smooth(ramp(t, ev.driveStart, ev.driveStart + 2.6));
    if (t < ev.driveAway) return CRUISE_W * (1 - smooth(ramp(t, ev.stop[0], ev.stop[1])));
    return 0.32 * smooth(ramp(t, ev.driveAway, ev.driveAway + 1.2));
  };
  const wheel = new Float64Array(n);
  const omegaW = new Float64Array(n);
  for (let f = 1; f < n; f++) {
    wheel[f] = wheel[f - 1] + (2 * PI * wheelSpeed((f - 0.5) / fps)) / fps;
    omegaW[f] = wheelSpeed(f / fps);
  }
  const at = (frame: number): EvDriveState => {
    const f = Math.max(0, Math.min(n - 1, Math.round(frame)));
    const t = f / fps;
    const w = omegaW[f];
    const accel = (wheelSpeed(t + 0.05) - wheelSpeed(t - 0.05)) / 0.1;
    return {
      wheel: wheel[f],
      omegaW: w,
      rotor: wheel[f] * RATIO,
      omegaR: w * RATIO,
      dist: wheel[f] * CAR.wheelR,
      power: Math.min(1, Math.max(0, w / CRUISE_W) * 0.55 + Math.max(0, accel) * 1.2),
    };
  };
  return { at, wheel, omegaW, ratio: RATIO };
};
export type EvDrive = ReturnType<typeof buildEvDrive>;

/** Current in stator phase k (0,1,2) — a field rotating with the rotor (PM synchronous motor). */
export const phaseCurrent = (rotor: number, k: number) => Math.cos(MOTOR.polePairs * rotor - (k * 2 * PI) / 3);
export const rotorLerp = lerp;
