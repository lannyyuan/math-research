/** Every sound in the electric-car video (same voice/volumes as the gasoline car; electronic blips; quiet motor whine). */
import { Audio } from "@remotion/media";
import React from "react";
import { staticFile, useVideoConfig } from "remotion";
import manifest from "./audio-manifest.json";
import { evLabelSchedule } from "./labels";
import type { EvTimeline } from "./timeline";

const sfx = (name: string) => staticFile(`sfx/${name}`);

export const ElectricCarSound: React.FC<{ readonly tl: EvTimeline; readonly narration: boolean }> = ({ tl, narration }) => {
  const { fps } = useVideoConfig();
  if (manifest.motorFrames !== tl.totalFrames) {
    throw new Error("Motor sound is stale for this timeline — run `npm run audio` (scripts/make-audio.ts).");
  }
  const f = (s: number) => Math.round(s * fps);
  const { ev } = tl;
  return (
    <>
      {/* quiet motor hum: pitch follows rotor speed, silent when the car stands still */}
      <Audio name="Motor hum" src={sfx("ev-motor.wav")} volume={0.3} />
      {narration
        ? tl.lines.map((l) => (
            <Audio
              key={`${l.seg}-${l.idx}`}
              name={`Narration ${l.seg} ${l.idx + 1}`}
              src={staticFile(`voice/electric-car/${l.file}`)}
              from={f(l.clipAt)}
              trimBefore={f(l.srcFrom)}
              trimAfter={f(l.srcTo)}
              premountFor={fps}
              volume={1}
            />
          ))
        : null}
      {evLabelSchedule(tl).map((l, i) => (
        <Audio key={`b${i}`} name="Label blip" src={sfx("blip.wav")} from={f(l.t0)} premountFor={fps} volume={0.3} />
      ))}
      <Audio name="Battery charge" src={sfx("charge.wav")} from={f(ev.modulesLit[0])} premountFor={fps} volume={0.3} />
      <Audio name="Current whoosh" src={sfx("current.wav")} from={f(ev.dcCurrent)} premountFor={fps} volume={0.4} />
      <Audio name="Current whoosh (motor)" src={sfx("current.wav")} from={f(ev.driveStart - 0.3)} premountFor={fps} volume={0.4} />
      <Audio name="Clean air" src={sfx("wind.wav")} from={f(ev.noExhaust)} premountFor={fps} volume={0.25} />
      <Audio name="Explode whoosh" src={sfx("whoosh.wav")} from={f(ev.explodeOut[0] - 0.1)} premountFor={fps} volume={0.5} />
      {ev.icons.map((t, i) => (
        <Audio key={`i${i}`} name="Icon pop" src={sfx("blip.wav")} from={f(t)} premountFor={fps} volume={0.45} />
      ))}
      <Audio name="Merge whoosh" src={sfx("whoosh-soft.wav")} from={f(ev.merge[0])} premountFor={fps} volume={0.45} />
      <Audio name="End chime" src={sfx("chime.wav")} from={f(tl.seg.end.start)} premountFor={fps} volume={0.45} />
    </>
  );
};
