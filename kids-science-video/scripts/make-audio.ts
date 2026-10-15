/**
 * Procedural sound design — no downloaded samples.
 *  - short UI/effect sounds (咔哒 click, whoosh, gear clunk, cool wind, puff, chime, soft "boop")
 *  - the engine hum for the gasoline-car video, synthesised from the SAME per-frame
 *    crank data the picture uses: one soft thump per cylinder firing, and a drone
 *    whose pitch follows engine speed → rhythm always matches the animation.
 * Run after the narration (timeline depends on it):  npx tsx scripts/make-audio.ts
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { GAS_DRIVE, GAS_TL } from "../src/gas-car/data";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SR = 44100;

// deterministic noise (no Math.random → identical files every run)
let seed = 12345;
const rnd = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
};
const noise = () => rnd() * 2 - 1;

const writeWav = (path: string, data: Float32Array) => {
  mkdirSync(dirname(path), { recursive: true });
  const buf = Buffer.alloc(44 + data.length * 2);
  buf.write("RIFF", 0);
  buf.writeUInt32LE(36 + data.length * 2, 4);
  buf.write("WAVE", 8);
  buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 2, 28);
  buf.writeUInt16LE(2, 32);
  buf.writeUInt16LE(16, 34);
  buf.write("data", 36);
  buf.writeUInt32LE(data.length * 2, 40);
  for (let i = 0; i < data.length; i++) buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, data[i])) * 32767), 44 + i * 2);
  writeFileSync(path, buf);
};

const normalize = (d: Float32Array, peak: number) => {
  let m = 0;
  for (const v of d) m = Math.max(m, Math.abs(v));
  if (m > 0) for (let i = 0; i < d.length; i++) d[i] *= peak / m;
  return d;
};
const fadeEdges = (d: Float32Array, ms = 4) => {
  const n = Math.round((SR * ms) / 1000);
  for (let i = 0; i < n && i < d.length; i++) {
    d[i] *= i / n;
    d[d.length - 1 - i] *= i / n;
  }
  return d;
};
const lowpass = (d: Float32Array, cutoff: (i: number) => number) => {
  let y = 0;
  for (let i = 0; i < d.length; i++) {
    const a = 1 - Math.exp((-2 * Math.PI * cutoff(i)) / SR);
    y += a * (d[i] - y);
    d[i] = y;
  }
  return d;
};
const len = (s: number) => new Float32Array(Math.round(s * SR));

// 咔哒: two tiny wooden ticks
const click = () => {
  const d = len(0.12);
  for (const [t0, f, a] of [
    [0, 2300, 1],
    [0.045, 1650, 0.6],
  ] as const) {
    for (let i = 0; i < d.length; i++) {
      const t = i / SR - t0;
      if (t < 0) continue;
      d[i] += a * Math.exp(-t / 0.008) * (Math.sin(2 * Math.PI * f * t) + 0.35 * noise());
    }
  }
  return fadeEdges(normalize(d, 0.8));
};

const whoosh = (dur: number, f0: number, f1: number) => {
  const d = len(dur);
  for (let i = 0; i < d.length; i++) d[i] = noise();
  lowpass(d, (i) => f0 + (f1 - f0) * Math.sin((Math.PI * i) / d.length));
  lowpass(d, (i) => f0 + (f1 - f0) * Math.sin((Math.PI * i) / d.length));
  for (let i = 0; i < d.length; i++) d[i] *= Math.pow(Math.sin((Math.PI * i) / d.length), 1.6);
  return fadeEdges(normalize(d, 0.7), 10);
};

const clunk = () => {
  const d = len(0.3);
  for (let i = 0; i < d.length; i++) {
    const t = i / SR;
    d[i] = Math.exp(-t / 0.05) * Math.sin(2 * Math.PI * (130 - 40 * t) * t) + 0.25 * Math.exp(-t / 0.01) * noise();
  }
  lowpass(d, () => 1800);
  return fadeEdges(normalize(d, 0.75));
};

const wind = () => {
  const d = len(3.2);
  for (let i = 0; i < d.length; i++) d[i] = noise();
  lowpass(d, (i) => 500 + 350 * Math.sin((i / SR) * 2.4));
  for (let i = 0; i < d.length; i++) {
    const u = i / d.length;
    d[i] *= Math.pow(Math.sin(Math.PI * u), 1.2) * (0.75 + 0.25 * Math.sin((i / SR) * 7.5));
  }
  return fadeEdges(normalize(d, 0.6), 20);
};

const puff = () => {
  const d = len(0.7);
  for (let i = 0; i < d.length; i++) d[i] = noise();
  lowpass(d, (i) => 380 - 200 * (i / d.length));
  for (let i = 0; i < d.length; i++) {
    const t = i / SR;
    d[i] *= (1 - Math.exp(-t / 0.03)) * Math.exp(-t / 0.18);
  }
  return fadeEdges(normalize(d, 0.6), 10);
};

const chime = () => {
  const d = len(1.6);
  for (const [t0, f] of [
    [0, 1046.5],
    [0.14, 1318.5],
    [0.28, 1568.0],
  ] as const) {
    for (let i = 0; i < d.length; i++) {
      const t = i / SR - t0;
      if (t < 0) continue;
      const env = Math.exp(-t / 0.45) * (1 - Math.exp(-t / 0.004));
      d[i] += env * (Math.sin(2 * Math.PI * f * t) + 0.3 * Math.sin(2 * Math.PI * 2 * f * t));
    }
  }
  return fadeEdges(normalize(d, 0.6), 10);
};

// soft, friendly "boop" for the narration's 砰 — deliberately not an explosion
const boop = () => {
  const d = len(0.35);
  let ph = 0;
  for (let i = 0; i < d.length; i++) {
    const t = i / SR;
    ph += (2 * Math.PI * (210 - 140 * Math.min(1, t / 0.14))) / SR;
    d[i] = Math.sin(ph) * (1 - Math.exp(-t / 0.005)) * Math.exp(-t / 0.09);
  }
  return fadeEdges(normalize(d, 0.7));
};

/** Engine hum from the drive data: drone pitch ∝ rpm, a soft thump at every firing. */
const engine = () => {
  const total = GAS_TL.totalFrames / GAS_TL.fps;
  const d = len(total);
  const fps = GAS_TL.fps;
  const omegaAt = (t: number) => {
    const f = t * fps;
    const i = Math.min(GAS_DRIVE.omegaE.length - 2, Math.floor(f));
    const u = f - i;
    return GAS_DRIVE.omegaE[i] * (1 - u) + GAS_DRIVE.omegaE[i + 1] * u;
  };
  let ph = 0;
  for (let i = 0; i < d.length; i++) {
    const t = i / SR;
    const w = omegaAt(t);
    const run = Math.min(1, w / 0.35);
    const f0 = 46 + 13 * w;
    ph += (2 * Math.PI * f0) / SR;
    d[i] = run * (0.5 * Math.sin(ph) + 0.25 * Math.sin(2 * ph + 0.3) + 0.12 * Math.sin(3 * ph + 1.1)) * (0.75 + 0.25 * Math.min(1, w));
  }
  // firing thumps
  const thumpLen = Math.round(0.16 * SR);
  for (const f of GAS_DRIVE.firings) {
    const s0 = Math.round(f.t * SR);
    const w = omegaAt(f.t);
    const amp = 0.9 * Math.min(1, w / 0.4);
    for (let k = 0; k < thumpLen && s0 + k < d.length; k++) {
      const t = k / SR;
      d[s0 + k] += amp * Math.exp(-t / 0.045) * (1 - Math.exp(-t / 0.003)) * (Math.sin(2 * Math.PI * 64 * t) + 0.2 * noise());
    }
  }
  lowpass(d, () => 900);
  return fadeEdges(normalize(d, 0.75), 30);
};

const out = (name: string) => join(ROOT, "public", "sfx", name);
writeWav(out("click.wav"), click());
writeWav(out("whoosh.wav"), whoosh(0.9, 300, 2600));
writeWav(out("whoosh-soft.wav"), whoosh(1.4, 200, 1300));
writeWav(out("clunk.wav"), clunk());
writeWav(out("wind.wav"), wind());
writeWav(out("puff.wav"), puff());
writeWav(out("chime.wav"), chime());
writeWav(out("boop.wav"), boop());
writeWav(out("gas-car-engine.wav"), engine());
writeFileSync(
  join(ROOT, "src", "gas-car", "audio-manifest.json"),
  JSON.stringify({ engineFrames: GAS_TL.totalFrames, firings: GAS_DRIVE.firings.length }, null, 2) + "\n",
);
console.log(`audio written; engine track ${GAS_TL.total.toFixed(2)}s, ${GAS_DRIVE.firings.length} firings`);
