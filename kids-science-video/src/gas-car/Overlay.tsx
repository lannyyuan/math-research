import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { BigTitle } from "../components/Cards";
import { Counter } from "../components/Counter";
import { LabelLayer } from "../components/LabelLayer";
import { ChipPanel, NumberTag } from "../components/Panels";
import { Subtitle } from "../components/Subtitle";
import { easeOutCubic, ramp, smooth, window } from "../lib/anim";
import { makeCamera, projectToScreen } from "../lib/camera";
import type { Rect } from "../lib/labelLayout";
import { COLORS } from "../style/theme";
import { cylinderTagAnchors, labelItems, labelSchedule } from "./labels";
import { FIRING_ORDER, type Drive } from "./mechanics";
import { cameraPose, sceneState } from "./state";
import type { Timeline } from "./timeline";

const recentFiring = (drive: Drive, t: number, cyl: number, hold = 0.32) => {
  let best = 0;
  // firings are sorted; scan back from the last one before t
  let lo = 0;
  let hi = drive.firings.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (drive.firings[mid].t <= t) lo = mid;
    else hi = mid - 1;
  }
  for (let k = lo; k >= 0 && k > lo - 6; k--) {
    const f = drive.firings[k];
    if (f.t > t) continue;
    if (f.cyl === cyl) best = Math.max(best, 1 - (t - f.t) / hold);
  }
  return Math.max(0, best);
};

/** Layout constants for the fixed UI so labels can avoid them. */
export const UI = {
  subtitle: { x0: 0, y0: 930, x1: 1920, y1: 1080 } as Rect,
  topRightPanel: { x0: 1250, y0: 40, x1: 1880, y1: 250 } as Rect,
  counter: { x0: 70, y0: 60, x1: 540, y1: 300 } as Rect,
  title: { x0: 260, y0: 70, x1: 1660, y1: 280 } as Rect,
};

/**
 * Subtitle for time t. Clauses that follow each other closely swap in place
 * (no fade gap → no flicker); a fade only happens at real pauses.
 */
export const currentSubtitle = (tl: Timeline, t: number) => {
  const lines = tl.lines;
  const chained = (a: (typeof lines)[number] | undefined, b: (typeof lines)[number] | undefined) =>
    !!a && !!b && a.seg === b.seg && b.speechStart - a.speechEnd < 0.9;
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    const prev = lines[i - 1];
    const next = lines[i + 1];
    const start = chained(prev, l) ? l.speechStart - 0.15 : l.speechStart - 0.25;
    const end = chained(l, next) ? next.speechStart - 0.15 : l.speechEnd + 0.9;
    if (t >= start && t < end) {
      const fin = chained(prev, l) ? 1 : smooth(ramp(t, start, start + 0.2));
      const fout = chained(l, next) ? 1 : 1 - smooth(ramp(t, end - 0.25, end));
      return { text: l.text, appear: Math.min(fin, fout) };
    }
  }
  return null;
};

export const GasCarOverlay: React.FC<{ readonly tl: Timeline; readonly drive: Drive }> = ({ tl, drive }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const st = sceneState(tl, drive, frame);
  const t = st.t;
  const { ev, seg } = tl;
  const pose = cameraPose(tl, t);
  const cam = makeCamera(pose, width, height);

  const firingAppear = window(t, ev.firingPanel[0], ev.firingPanel[1], 0.35, 0.4);
  const gearAppear = window(t, ev.gearPanel[0], ev.gearPanel[1], 0.35, 0.4);
  const counterAppear = window(t, ev.labelsIn - 0.1, ev.labelsOut + 0.5, 0.35, 0.4);
  const sub = currentSubtitle(tl, t);

  const tags = cylinderTagAnchors().map((a, i) => ({ ...projectToScreen(cam, a, width, height), cyl: i + 1 }));
  const reserved: Rect[] = [UI.subtitle];
  if (firingAppear > 0 || gearAppear > 0) reserved.push(UI.topRightPanel);
  if (counterAppear > 0) reserved.push(UI.counter);
  if (t < seg.title.end + 0.3 || t > seg.end.start - 0.2) reserved.push(UI.title);
  if (firingAppear > 0) for (const g of tags) reserved.push({ x0: g.x - 34, y0: g.y - 34, x1: g.x + 34, y1: g.y + 34 });

  const items = labelItems(labelSchedule(tl), st);
  const engaged = st.drive.shiftU >= 0.5 ? st.drive.gear : st.drive.gearFrom;

  return (
    <AbsoluteFill>
      <LabelLayer items={items} pose={pose} width={width} height={height} reserved={reserved} />

      {tags.map((g) => (
        <NumberTag key={g.cyl} x={g.x} y={g.y} label={String(g.cyl)} active={recentFiring(drive, t, g.cyl)} appear={firingAppear} />
      ))}
      <ChipPanel
        title="点火顺序"
        color={COLORS.carOrange}
        appear={firingAppear}
        chips={FIRING_ORDER.map((c) => ({ label: String(c), active: recentFiring(drive, t, c) }))}
      />
      <ChipPanel
        title="变速箱 · 换挡"
        color={COLORS.gearbox}
        appear={gearAppear * (1 - firingAppear)}
        arrows
        chips={[1, 2, 3].map((g) => ({ label: `${g}档`, active: engaged === g ? 1 : 0 }))}
      />
      <Counter
        title="会动的零件"
        target={2000}
        progress={easeOutCubic(ramp(t, ev.counter[0], ev.counter[1]))}
        done={smooth(ramp(t, ev.counter[1] - 0.1, ev.counter[1] + 0.3))}
        appear={counterAppear}
        left={UI.counter.x0}
        top={UI.counter.y0}
      />

      <BigTitle text="汽油车的肚子里有什么？" t={t} start={0.1} end={seg.title.end + 0.25} top={86} />
      <BigTitle text="汽油车 = 复杂的小工厂" t={t} start={seg.end.start + 0.05} end={tl.total + 5} top={86} />

      {sub ? <Subtitle text={sub.text} appear={sub.appear} /> : null}
    </AbsoluteFill>
  );
};
