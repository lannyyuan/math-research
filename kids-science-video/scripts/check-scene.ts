/**
 * Automated invariant checks for the gasoline-car video (run before rendering):
 *   npx tsx scripts/check-scene.ts
 * Exits non-zero if any invariant fails.
 */
import { Vector3 } from "three";
import { placeLabels } from "../src/components/LabelLayer";
import { findOverlaps, rectOf } from "../src/lib/labelLayout";
import { CAR } from "../src/three/car/carLayout";
import { GAS_DRIVE, GAS_TL } from "../src/gas-car/data";
import { cylinderTagAnchors, labelItems, labelSchedule } from "../src/gas-car/labels";
import { ENG } from "../src/gas-car/layout";
import { crankPin, FIRE_AT, pistonPinY, sinceFire, sparkFlash, valveLift } from "../src/gas-car/mechanics";
import { UI } from "../src/gas-car/Overlay";
import { PART_IDS, PARTS, WHEEL_EXPLODE } from "../src/gas-car/parts";
import { cameraPose, sceneState } from "../src/gas-car/state";
import { makeCamera, projectToScreen } from "../src/lib/camera";
import manifest from "../src/gas-car/audio-manifest.json";

const W = 1920;
const H = 1080;
let failures = 0;
const fail = (msg: string) => {
  failures++;
  console.log("  ✗ " + msg);
};
const ok = (msg: string) => console.log("  ✓ " + msg);
const tl = GAS_TL;
const drive = GAS_DRIVE;
const N = tl.totalFrames;

console.log(`Timeline: ${tl.total.toFixed(2)} s, ${N} frames`);
if (tl.total < 60 || tl.total > 80) fail("total length outside 60–80 s");
else ok("total length within 60–80 s");

// ---------------------------------------------------------------- mechanics
console.log("Mechanics");
{
  let maxRodErr = 0;
  let tdcErr = 0;
  let badFlash = 0;
  let badValve = 0;
  for (let f = 0; f <= N; f++) {
    const s = drive.at(f);
    for (let i = 0; i < 4; i++) {
      const cp = crankPin(s.theta, i);
      const py = pistonPinY(s.theta, i);
      maxRodErr = Math.max(maxRodErr, Math.abs(Math.hypot(ENG.x - cp.x, py - cp.y) - ENG.rod));
      const fl = sparkFlash(s.theta, i, s.omegaE);
      const p = sinceFire(s.theta, i);
      if (fl > 0 && !(p < 0.9 || p > 4 * Math.PI - 0.12)) badFlash++;
      // valves must be shut around the firing TDC (compression/power), open only in their own stroke
      const li = valveLift(s.theta, i, "intake");
      const le = valveLift(s.theta, i, "exhaust");
      if ((p < 0.5 || p > 4 * Math.PI - 0.5) && (li > 1e-6 || le > 1e-6)) badValve++;
      if (li > 1e-6 && !(p > 2.5 * Math.PI - (2 * Math.PI) / 3 - 1e-6 && p < 2.5 * Math.PI + (2 * Math.PI) / 3 + 1e-6)) badValve++;
      if (le > 1e-6 && !(p > 1.5 * Math.PI - (2 * Math.PI) / 3 - 1e-6 && p < 1.5 * Math.PI + (2 * Math.PI) / 3 + 1e-6)) badValve++;
    }
  }
  // at each cylinder's firing angle its piston is at the top (TDC)
  for (let i = 0; i < 4; i++) {
    const top = pistonPinY(FIRE_AT[i], i);
    tdcErr = Math.max(tdcErr, Math.abs(top - (ENG.crankY + ENG.throw + ENG.rod)));
  }
  maxRodErr < 1e-9 ? ok(`connecting rod length constant (max err ${maxRodErr.toExponential(1)})`) : fail(`rod length error ${maxRodErr}`);
  tdcErr < 1e-9 ? ok("each cylinder fires at its own TDC") : fail(`TDC error ${tdcErr}`);
  badFlash === 0 ? ok("spark flashes only at the cylinder's own firing point") : fail(`${badFlash} stray spark frames`);
  badValve === 0 ? ok("valves open only in their own stroke (cam = crank/2)") : fail(`${badValve} valve timing violations`);

  const seq = drive.firings.map((x) => x.cyl);
  const order = [1, 3, 4, 2];
  let orderOk = seq.length > 8;
  for (let k = 1; k < seq.length; k++) {
    const a = order.indexOf(seq[k - 1]);
    if (order[(a + 1) % 4] !== seq[k]) orderOk = false;
  }
  orderOk ? ok(`firing order 1-3-4-2 over ${seq.length} firings`) : fail("firing order broken");

  // a firing lands on the narration's 砰
  const near = drive.firings.some((x) => Math.abs(x.t - tl.ev.peng) < 0.5 / tl.fps);
  near ? ok("a cylinder fires exactly on “砰”") : fail("no firing on 砰");

  // drivetrain: engaged & settled ⇒ ω_engine = ratio · ω_wheel
  let worst = 0;
  for (let f = 0; f <= N; f++) {
    const s = drive.at(f);
    if (s.gear > 0 && s.shiftU >= 1 && s.omegaW > 0.05) {
      const want = drive.ratios[s.gear - 1] * s.omegaW;
      if (want > 1.0) worst = Math.max(worst, Math.abs(s.omegaE - want) / want);
    }
  }
  worst < 0.02 ? ok(`wheel speed matches engine speed ÷ gear ratio (max dev ${(worst * 100).toFixed(2)}%)`) : fail(`drivetrain mismatch ${worst}`);
  manifest.engineFrames === N ? ok("engine sound generated for this timeline") : fail("engine sound is stale → npx tsx scripts/make-audio.ts");
}

// ---------------------------------------------------------------- exploded view
console.log("Exploded view");
{
  const c = new Vector3(...CAR.center);
  for (const id of PART_IDS) {
    if (id === "wheels") continue;
    const a = new Vector3(...PARTS[id].anchor);
    const o = new Vector3(...PARTS[id].explode);
    const cos = o.clone().normalize().dot(a.clone().sub(c).normalize());
    if (!(cos > 0)) fail(`${id} does not move away from the car centre (cos ${cos.toFixed(2)})`);
  }
  for (const [k, o] of Object.entries(WHEEL_EXPLODE)) {
    const w = { FL: [CAR.frontAxleX, -CAR.trackHalf], FR: [CAR.frontAxleX, CAR.trackHalf], RL: [CAR.rearAxleX, -CAR.trackHalf], RR: [CAR.rearAxleX, CAR.trackHalf] }[k]!;
    if (o[0] * w[0] + o[2] * w[1] <= 0) fail(`wheel ${k} not outward`);
  }
  ok("every part's explode direction points away from the car centre");
  const after = sceneState(tl, drive, Math.round(tl.ev.merge[1] * tl.fps) + 1).explode;
  const before = sceneState(tl, drive, Math.round(tl.ev.explodeOut[0] * tl.fps) - 1).explode;
  after === 0 && before === 0 ? ok("parts sit exactly at their original positions before and after (offset = 0)") : fail(`explode not zero: ${before} / ${after}`);
  let mono = true;
  let prevE = 0;
  for (let f = Math.round(tl.ev.explodeOut[0] * tl.fps); f <= Math.round(tl.ev.explodeOut[1] * tl.fps); f++) {
    const e = sceneState(tl, drive, f).explode;
    if (e < prevE - 1e-12) mono = false;
    prevE = e;
  }
  mono ? ok("parts slide outwards monotonically") : fail("explode not monotonic");
}

// ---------------------------------------------------------------- labels
console.log("Labels");
{
  const sched = labelSchedule(tl);
  let overlapFrames = 0;
  let outFrames = 0;
  let reservedHits = 0;
  let offscreenAnchors = 0;
  const examples: string[] = [];
  for (let f = 0; f <= N; f++) {
    const st = sceneState(tl, drive, f);
    const t = st.t;
    const items = labelItems(sched, st);
    if (!items.length) continue;
    const pose = cameraPose(tl, t);
    const reserved = [UI.subtitle];
    const firing = t >= tl.ev.firingPanel[0] && t <= tl.ev.firingPanel[1];
    const gear = t >= tl.ev.gearPanel[0] && t <= tl.ev.gearPanel[1];
    if (firing || gear) reserved.push(UI.topRightPanel);
    if (t >= tl.ev.labelsIn - 0.1 && t <= tl.ev.labelsOut + 0.5) reserved.push(UI.counter);
    if (firing) {
      const cam = makeCamera(pose, W, H);
      for (const a of cylinderTagAnchors()) {
        const p = projectToScreen(cam, a, W, H);
        reserved.push({ x0: p.x - 34, y0: p.y - 34, x1: p.x + 34, y1: p.y + 34 });
      }
    }
    const placed = placeLabels(items, pose, W, H, reserved).filter((p) => p.item.opacity > 0.5);
    const ov = findOverlaps(placed);
    if (ov.length) {
      overlapFrames++;
      if (examples.length < 5) examples.push(`frame ${f}: ${ov.map((x) => x.join("/")).join(", ")}`);
    }
    for (const p of placed) {
      const r = rectOf(p);
      if (r.x0 < 0 || r.y0 < 0 || r.x1 > W || r.y1 > H) outFrames++;
      if (p.ax < 0 || p.ax > W || p.ay < 0 || p.ay > H) offscreenAnchors++;
      for (const q of reserved) if (Math.min(r.x1, q.x1) - Math.max(r.x0, q.x0) > 0 && Math.min(r.y1, q.y1) - Math.max(r.y0, q.y0) > 0) reservedHits++;
    }
  }
  overlapFrames === 0 ? ok("labels never overlap each other") : fail(`labels overlap in ${overlapFrames} frames\n      ${examples.join("\n      ")}`);
  outFrames === 0 ? ok("labels always inside the frame") : fail(`${outFrames} label-frames outside the frame`);
  reservedHits === 0 ? ok("labels never cover subtitles / panels / counter") : fail(`${reservedHits} label-frames cover reserved UI`);
  offscreenAnchors === 0 ? ok("every label points at something on screen") : fail(`${offscreenAnchors} label anchors off screen`);
}

console.log(failures ? `\n${failures} check(s) FAILED` : "\nAll checks passed.");
process.exit(failures ? 1 : 0);
