/** Every sound in the gasoline-car video, placed from the same timeline the picture uses. */
import { Audio } from "@remotion/media";
import React from "react";
import { staticFile, useVideoConfig } from "remotion";
import manifest from "./audio-manifest.json";
import { labelSchedule } from "./labels";
import type { Timeline } from "./timeline";

const sfx = (name: string) => staticFile(`sfx/${name}`);

export const GasCarSound: React.FC<{ readonly tl: Timeline; readonly narration: boolean }> = ({ tl, narration }) => {
  const { fps } = useVideoConfig();
  if (manifest.engineFrames !== tl.totalFrames) {
    throw new Error("Engine sound is stale for this timeline — run `npm run audio` (scripts/make-audio.ts).");
  }
  const f = (s: number) => Math.round(s * fps);
  const { ev } = tl;
  const clicks = labelSchedule(tl).map((l) => l.t0);
  return (
    <>
      {/* soft engine hum: rhythm = cylinder firings, pitch = engine speed */}
      <Audio name="Engine hum" src={sfx("gas-car-engine.wav")} volume={0.32} />

      {narration
        ? tl.lines.map((l) => (
            <Audio
              key={`${l.seg}-${l.idx}`}
              name={`Narration ${l.seg} ${l.idx + 1}`}
              src={staticFile(`voice/gas-car/${l.file}`)}
              from={f(l.clipAt)}
              trimBefore={f(l.srcFrom)}
              trimAfter={f(l.srcTo)}
              premountFor={fps}
              volume={1}
            />
          ))
        : null}

      {clicks.map((t, i) => (
        <Audio key={`c${i}`} name="Label click" src={sfx("click.wav")} from={f(t)} premountFor={fps} volume={0.32} />
      ))}
      <Audio name="Fuel whoosh" src={sfx("whoosh.wav")} from={f(ev.fuelFlow - 0.15)} premountFor={fps} volume={0.38} />
      <Audio name="Boop" src={sfx("boop.wav")} from={f(ev.peng)} premountFor={fps} volume={0.45} />
      {[ev.driveStart - 0.4, ev.shift1, ev.shift2].map((t) => (
        <Audio key={t} name="Gear clunk" src={sfx("clunk.wav")} from={f(t)} premountFor={fps} volume={0.5} />
      ))}
      <Audio name="Cool wind" src={sfx("wind.wav")} from={f(ev.radiatorHL)} premountFor={fps} volume={0.32} />
      <Audio name="Exhaust puff" src={sfx("puff.wav")} from={f(ev.exhaustHL + 0.3)} premountFor={fps} volume={0.35} />
      <Audio name="Explode whoosh" src={sfx("whoosh.wav")} from={f(ev.explodeOut[0] - 0.1)} premountFor={fps} volume={0.5} />
      <Audio name="Counter chime" src={sfx("chime.wav")} from={f(ev.counter[1] - 0.05)} premountFor={fps} volume={0.35} />
      <Audio name="Merge whoosh" src={sfx("whoosh-soft.wav")} from={f(ev.merge[0])} premountFor={fps} volume={0.45} />
      <Audio name="End chime" src={sfx("chime.wav")} from={f(tl.seg.end.start)} premountFor={fps} volume={0.45} />
    </>
  );
};
