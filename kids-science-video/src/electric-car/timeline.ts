/** "What happens when" for the electric-car video — mirrors the gasoline-car timeline. */
import type { CamKey, CamPose } from "../lib/camera";
import { scheduleNarration, type VoiceTiming } from "../lib/narration";
import { EV_TEARDOWN } from "./parts";

export const EV_SEG_ORDER = ["title", "battery", "controller", "motor", "reducer", "rear", "explode", "end"] as const;
export type EvSegId = (typeof EV_SEG_ORDER)[number];

const TARGET: Record<EvSegId, number> = { title: 2, battery: 12, controller: 12, motor: 14, reducer: 10, rear: 10, explode: 10, end: 2 };
const LINE_AT: Partial<Record<EvSegId, (number | null)[]>> = {
  battery: [0.9, null, null],
  controller: [1.8, null, null],
  motor: [2.2, null, null],
  reducer: [1.7, null, null],
  rear: [1.3, null, null, null],
  explode: [0.5, null, null, null],
};

export const buildEvTimeline = (voice: VoiceTiming, fps = 30) => {
  const n = scheduleNarration({ order: EV_SEG_ORDER, target: TARGET, lineAt: LINE_AT, voice, fps });
  const { seg, line, wordAt } = n;
  const B = seg.battery.start;
  const C = seg.controller.start;
  const M = seg.motor.start;
  const R = seg.reducer.start;
  const Q = seg.rear.start;
  const X = seg.explode.start;
  const N = seg.end.start;
  // staggered teardown: last departure + one leg
  const spread = EV_TEARDOWN;

  const ev = {
    xrayOn: [B + 0.05, B + 0.95] as const,
    xrayOff: [N - 0.7, N + 0.15] as const,
    // battery
    batteryHL: line("battery", 0).speechStart - 0.25,
    modulesLit: [line("battery", 1).speechStart - 0.3, line("battery", 2).speechEnd] as const,
    // controller
    controllerHL: line("controller", 0).speechStart - 0.15,
    dcCurrent: C + 1.0,
    harnessLabel: line("controller", 1).speechStart - 0.1,
    // motor
    motorHL: line("motor", 0).speechStart - 0.15,
    driveStart: line("motor", 1).speechStart - 0.25,
    statorRotor: line("motor", 2).speechStart - 0.1,
    // reducer
    reducerHL: line("reducer", 0).speechStart - 0.15,
    ratioPanel: [line("reducer", 0).speechStart + 0.4, Q + 0.2] as const,
    wheelsShow: line("reducer", 1).speechStart - 0.3,
    // rear
    rearCam: Q,
    noExhaust: line("rear", 1).speechStart - 0.15,
    compare: [line("rear", 1).speechStart - 0.1, line("rear", 2).speechEnd + 0.2] as const,
    leaf: line("rear", 3).speechStart - 0.2,
    // exploded view
    stop: [X, X + 0.8] as const,
    explodeOut: [X + 0.35, X + 0.35 + spread] as const,
    labelsIn: X + 0.35 + spread - 0.15,
    icons: [wordAt("explode", "电池"), wordAt("explode", "电机"), wordAt("explode", "电控")] as const,
    counter: [X + 0.35 + spread, line("explode", 2).speechEnd] as const,
    labelsOut: line("explode", 3).speechStart - 0.45,
    merge: [line("explode", 3).speechStart - 0.2, line("explode", 3).speechStart - 0.2 + spread] as const,
    driveAway: line("explode", 3).speechStart - 0.2 + spread + 0.15,
    smile: N - 0.4,
  };

  // Shared framing with the gasoline car (hero, side, rear, explode, end are identical poses)
  const CAM: Record<string, CamPose> = {
    hero: { pos: [6.2, 1.9, 7.0], target: [0.15, 0.72, 0], fov: 30 },
    side: { pos: [0.05, 1.45, 8.4], target: [0.05, 0.68, 0], fov: 30 },
    // the pack lies flat under the floor → look down a little more than the gasoline car's side view
    sideHigh: { pos: [0.05, 2.75, 7.9], target: [0.05, 0.5, 0], fov: 30 },
    controller: { pos: [3.15, 1.75, 1.95], target: [1.12, 0.52, 0.05], fov: 32 },
    controllerDrift: { pos: [3.05, 1.8, 1.75], target: [1.15, 0.52, 0.05], fov: 32 },
    // looking at the motor's end face past the right front wheel
    motor: { pos: [2.25, 0.84, 1.32], target: [1.43, 0.47, 0.3], fov: 24 },
    motorDrift: { pos: [2.3, 0.88, 1.24], target: [1.43, 0.47, 0.28], fov: 24 },
    // looking at the reducer's gear faces past the left front wheel
    reducer: { pos: [2.25, 0.86, -1.32], target: [1.37, 0.43, -0.27], fov: 25 },
    axle: { pos: [3.9, 2.3, -2.4], target: [1.2, 0.42, 0.0], fov: 32 },
    rear: { pos: [-4.4, 1.9, 4.9], target: [0.1, 0.45, 0], fov: 34 },
    explode: { pos: [3.85, 2.75, 6.3], target: [1.0, 0.78, 0.0], fov: 36 },
    explodeDrift: { pos: [3.7, 2.8, 6.4], target: [1.0, 0.78, 0.0], fov: 36 },
    endHero: { pos: [6.6, 1.7, 5.4], target: [0.3, 0.7, 0], fov: 30 },
  };
  const camKeys: CamKey[] = [
    { t: 0, pose: CAM.hero },
    { t: seg.title.end - 0.2, pose: CAM.side },
    { t: B + 1.6, pose: CAM.sideHigh },
    { t: C, pose: CAM.sideHigh },
    { t: C + 1.8, pose: CAM.controller },
    { t: M - 0.2, pose: CAM.controllerDrift },
    { t: M + 2.0, pose: CAM.motor },
    { t: R - 0.2, pose: CAM.motorDrift },
    { t: R + 1.6, pose: CAM.reducer },
    { t: ev.wheelsShow, pose: CAM.reducer },
    { t: ev.wheelsShow + 1.6, pose: CAM.axle },
    { t: Q, pose: CAM.axle },
    { t: Q + 1.4, pose: CAM.rear },
    { t: X, pose: CAM.rear },
    { t: X + 1.4, pose: CAM.explode },
    { t: ev.merge[1], pose: CAM.explodeDrift },
    { t: N - 0.9, pose: CAM.explodeDrift },
    { t: N + 0.9, pose: CAM.endHero },
  ];
  return { fps, ...n, ev, camKeys };
};

export type EvTimeline = ReturnType<typeof buildEvTimeline>;
