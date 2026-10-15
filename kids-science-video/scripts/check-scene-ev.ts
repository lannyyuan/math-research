/**
 * Invariant checks for the electric-car video:  npx tsx scripts/check-scene-ev.ts
 */
import { Vector3 } from "three";
import { placeLabels } from "../src/components/LabelLayer";
import { findOverlaps, rectOf } from "../src/lib/labelLayout";
import { CAR } from "../src/three/car/carLayout";
import { EV_DRIVE, EV_TL } from "../src/electric-car/data";
import { evLabelItems, evLabelSchedule } from "../src/electric-car/labels";
import { MOTOR, RATIO, RED } from "../src/electric-car/layout";
import { evReserved, leafBoxAt } from "../src/electric-car/Overlay";
import { EV_PART_IDS, EV_PARTS, EV_WHEEL_EXPLODE } from "../src/electric-car/parts";
import { evCameraPose, evState } from "../src/electric-car/state";
import { GAS_TL } from "../src/gas-car/data";
import manifest from "../src/electric-car/audio-manifest.json";

const W = 1920;
const H = 1080;
let failures = 0;
const fail = (m: string) => {
  failures++;
  console.log("  ✗ " + m);
};
const ok = (m: string) => console.log("  ✓ " + m);
const tl = EV_TL;
const N = tl.totalFrames;

console.log(`Timeline: ${tl.total.toFixed(2)} s, ${N} frames (gasoline car: ${GAS_TL.total.toFixed(2)} s)`);
tl.total >= 60 && tl.total <= 80 ? ok("total length within 60–80 s") : fail("total length outside 60–80 s");

console.log("Drivetrain");
{
  const dist = Math.hypot(MOTOR.x - RED.diffX, MOTOR.y - RED.diffY);
  const want = (RED.module * (RED.nPinion + RED.nGear)) / 2;
  Math.abs(dist - want) < 1e-9 ? ok(`gear centre distance = pitch radii sum (${want.toFixed(3)} m)`) : fail(`centre distance ${dist} ≠ ${want}`);
  let maxErr = 0;
  let speedErr = 0;
  for (let f = 0; f <= N; f++) {
    const s = EV_DRIVE.at(f);
    // pinion rotation.z = +rotor, big gear rotation.z = −rotor·nP/nG (+const) = −wheel → opposite senses, ratio exact
    const gear = -s.rotor * (RED.nPinion / RED.nGear);
    maxErr = Math.max(maxErr, Math.abs(gear + s.wheel));
    speedErr = Math.max(speedErr, Math.abs(s.omegaR - RATIO * s.omegaW));
  }
  maxErr < 1e-9 && speedErr < 1e-9
    ? ok(`rotor turns ${RATIO}× the wheel speed, gears mesh in opposite directions (max err ${maxErr.toExponential(1)})`)
    : fail(`reducer coupling error ${maxErr} / ${speedErr}`);
  let wrong = 0;
  let stillPowered = 0;
  for (let f = 0; f <= N; f++) {
    const st = evState(tl, EV_DRIVE, f);
    // current reaches the motor only while it also flows battery → controller
    if (st.acCurrent > 0.02 && st.dcCurrent < st.acCurrent * 0.5) wrong++;
    if (st.drive.omegaW > 0.01 && st.acCurrent < 0.01 && st.explode === 0 && st.t < tl.ev.stop[0]) stillPowered++;
  }
  wrong === 0 ? ok("current always flows battery → controller → motor") : fail(`${wrong} frames feed the motor without battery→controller current`);
  stillPowered === 0 ? ok("motor is powered whenever it drives the wheels") : fail(`${stillPowered} frames drive without power`);
  manifest.motorFrames === N ? ok("motor sound generated for this timeline") : fail("motor sound stale → npm run audio");
}

console.log("Exploded view");
{
  const c = new Vector3(...CAR.center);
  for (const id of EV_PART_IDS) {
    if (id === "wheels") continue;
    const cos = new Vector3(...EV_PARTS[id].explode).normalize().dot(new Vector3(...EV_PARTS[id].anchor).sub(c).normalize());
    if (!(cos > 0)) fail(`${id} does not move away from the car centre`);
  }
  for (const [k, o] of Object.entries(EV_WHEEL_EXPLODE)) {
    const w = { FL: [CAR.frontAxleX, -CAR.trackHalf], FR: [CAR.frontAxleX, CAR.trackHalf], RL: [CAR.rearAxleX, -CAR.trackHalf], RR: [CAR.rearAxleX, CAR.trackHalf] }[k]!;
    if (o[0] * w[0] + o[2] * w[1] <= 0) fail(`wheel ${k} not outward`);
  }
  ok("every block's explode direction points away from the car centre");
  const after = evState(tl, EV_DRIVE, Math.round(tl.ev.merge[1] * tl.fps) + 1).explode;
  const before = evState(tl, EV_DRIVE, Math.round(tl.ev.explodeOut[0] * tl.fps) - 1).explode;
  after === 0 && before === 0 ? ok("blocks sit exactly at their original positions before and after") : fail(`explode not zero ${before}/${after}`);
  ok(`${EV_PART_IDS.length} big blocks (gasoline car: 15) — "parts cloud vs a few blocks"`);
}

console.log("Labels");
{
  const sched = evLabelSchedule(tl);
  let overlapFrames = 0;
  let outFrames = 0;
  let reservedHits = 0;
  const ex: string[] = [];
  for (let f = 0; f <= N; f++) {
    const st = evState(tl, EV_DRIVE, f);
    const items = evLabelItems(sched, st);
    if (!items.length) continue;
    const leaf = leafBoxAt(tl, st.t, W, H);
    const reserved = evReserved(tl, st.t, leaf ? leaf.rect : null);
    const placed = placeLabels(items, evCameraPose(tl, st.t), W, H, reserved).filter((p) => p.item.opacity > 0.5);
    const ov = findOverlaps(placed);
    if (ov.length) {
      overlapFrames++;
      if (ex.length < 5) ex.push(`frame ${f}: ${ov.map((x) => x.join("/")).join(", ")}`);
    }
    for (const p of placed) {
      const r = rectOf(p);
      if (r.x0 < 0 || r.y0 < 0 || r.x1 > W || r.y1 > H) outFrames++;
      for (const q of reserved) if (Math.min(r.x1, q.x1) - Math.max(r.x0, q.x0) > 0 && Math.min(r.y1, q.y1) - Math.max(r.y0, q.y0) > 0) reservedHits++;
    }
  }
  overlapFrames === 0 ? ok("labels never overlap each other") : fail(`labels overlap in ${overlapFrames} frames\n      ${ex.join("\n      ")}`);
  outFrames === 0 ? ok("labels always inside the frame") : fail(`${outFrames} label-frames outside the frame`);
  reservedHits === 0 ? ok("labels never cover subtitles / panels / counter / icons") : fail(`${reservedHits} label-frames cover reserved UI`);
}
console.log(failures ? `\n${failures} check(s) FAILED` : "\nAll checks passed.");
process.exit(failures ? 1 : 0);
