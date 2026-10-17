/**
 * Geometric audit of the electric car (rest, apart and every frame of the explode
 * and merge):  npx tsx scripts/audit-ev.ts   → exits 1 on any problem.
 *  - clearance: no two assemblies interpenetrate (declared joints may slide apart along their axis)
 *  - terminals: every cable end lands on its host at rest
 *  - ground:    nothing dips below the floor
 *  - outward:   each assembly's distance from the car centre never shrinks while it explodes
 */
import { CAR } from "../src/three/car/carLayout";
import { EV_DRIVE, EV_TL } from "../src/electric-car/data";
import { EV_PART_IDS, EV_PARTS } from "../src/electric-car/parts";
import { PLUGS } from "../src/electric-car/layout";
import { EV_MOUNTS, evCableEnds, evShapes } from "../src/electric-car/shapes";
import { evGroupOffset, evState } from "../src/electric-car/state";
import { bounds, checkPose, prepare, sdf, vec, type Violation } from "../src/lib/sdfAudit";

type V3 = readonly [number, number, number];
const tl = EV_TL;
const shapes = evShapes();
const P = prepare(shapes, 0.02);
let failures = 0;
const fail = (m: string) => {
  failures++;
  console.log("  ✗ " + m);
};
const ok = (m: string) => console.log("  ✓ " + m);

const offsetsAt = (frame: number) => {
  const st = evState(tl, EV_DRIVE, frame);
  return (g: string): V3 => (g === "static" ? [0, 0, 0] : evGroupOffset(g, st));
};

// --- frames to replay: everything from just before the explode to just after the merge
const f0 = Math.floor((tl.ev.explodeOut[0] - 0.1) * tl.fps);
const f1 = Math.ceil((tl.ev.merge[1] + 0.1) * tl.fps);
const fApart = Math.round(((tl.ev.explodeOut[1] + tl.ev.merge[0]) / 2) * tl.fps);
console.log(`EV geometric audit: ${shapes.length} shapes, ${P.reduce((n, p) => n + p.pts.length, 0)} surface samples, frames ${f0}–${f1}`);

const summarize = (label: string, v: Violation[]) => {
  if (!v.length) return ok(`${label}: no interpenetration`);
  const byPair = new Map<string, Violation & { frames: number }>();
  for (const x of v) {
    const k = [x.a.split("#")[0], x.b.split("#")[0]].sort().join(" ↔ ");
    const prev = byPair.get(k);
    if (!prev || prev.depth < x.depth) byPair.set(k, { ...x, frames: (prev?.frames ?? 0) + 1 });
    else prev.frames++;
  }
  fail(`${label}: ${byPair.size} part pairs interpenetrate`);
  for (const [k, x] of [...byPair].sort((a, b) => b[1].depth - a[1].depth).slice(0, 25))
    console.log(`      ${k}  depth ${(x.depth * 100).toFixed(1)} cm  (${x.frames} hits, e.g. ${x.at})`);
};

// rest
summarize("assembled (rest)", checkPose(P, offsetsAt(f0), EV_MOUNTS, `frame ${f0}`));
// apart: also demand a visible gap between assemblies
{
  const v = checkPose(P, offsetsAt(fApart), [], `frame ${fApart}`, -0.01);
  summarize("apart (≥ 1 cm gap between every assembly)", v);
}
// mid-flight
{
  const all: Violation[] = [];
  for (let f = f0; f <= f1; f++) all.push(...checkPose(P, offsetsAt(f), EV_MOUNTS, `frame ${f}`));
  summarize(`explode + merge, every frame (${f1 - f0 + 1} frames)`, all);
}
// terminals: connector shells sit flush on a host of another assembly; cables end on a shell
{
  let bad = 0;
  for (const pl of PLUGS) {
    const host = shapes.filter((x) => x.group !== "harness" && x.group !== "static").map((x) => ({ x, d: sdf(x, pl.a) })).sort((a, b) => Math.abs(a.d) - Math.abs(b.d))[0];
    if (Math.abs(host.d) > 0.004) {
      bad++;
      console.log(`      plug at [${pl.a.map((v) => v.toFixed(3))}] is ${(host.d * 100).toFixed(1)} cm off its nearest host ${host.x.name}`);
    }
  }
  for (const e of evCableEnds()) {
    if (!PLUGS.some((pl) => vec.len(vec.sub(pl.b, e)) < 1e-6)) {
      bad++;
      console.log(`      cable end [${e.map((v) => v.toFixed(3))}] does not end on a connector shell`);
    }
  }
  bad ? fail(`${bad} cable ends are not seated`) : ok(`every cable ends on a connector shell seated flush on its host (${PLUGS.length} plugs)`);
}
// ground + outward
{
  let below = 0;
  let inward = 0;
  const c = CAR.center;
  const prevDist = new Map<string, number>();
  for (let f = f0; f <= f1; f++) {
    const off = offsetsAt(f);
    for (const s of shapes) {
      if (s.group === "static") continue;
      if (bounds(s).min[1] + off(s.group)[1] < -1e-6) below++;
    }
    if (f <= Math.round(tl.ev.explodeOut[1] * tl.fps) + 1)
      for (const [id, anchor, group] of [
        ...EV_PART_IDS.filter((x) => x !== "wheels").map((id) => [id, EV_PARTS[id].anchor, id === "halfShafts" ? "halfShaftR" : id] as const),
        ["halfShaftL", [1.32, 0.36, -0.48], "halfShaftL"] as const,
        ...["FL", "FR", "RL", "RR"].map((w) => [`wheel${w}`, [w[0] === "F" ? 1.32 : -1.33, 0.36, w[1] === "L" ? -0.75 : 0.75], `wheel${w}`] as const),
      ]) {
        const p = vec.add(anchor, off(group));
        const d = vec.len(vec.sub(p, c));
        if (d < (prevDist.get(id) ?? 0) - 1e-9) {
          inward++;
          if (inward <= 5) console.log(`      ${id} moves inwards at frame ${f}`);
        }
        prevDist.set(id, d);
      }
  }
  below ? fail(`${below} shape-frames dip below the floor`) : ok("nothing goes below the floor");
  inward ? fail(`${inward} frames where an assembly moves back towards the car centre while exploding`) : ok("every assembly only moves away from the car centre while exploding");
}
console.log(failures ? `\n${failures} audit check(s) FAILED` : "\naudit passed");
process.exit(failures ? 1 : 0);
