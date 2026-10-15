import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { BigTitle } from "../components/Cards";
import { Counter } from "../components/Counter";
import { BatteryIcon, CarSilhouette, ChipIcon, IconCard, LeafIcon, MotorIcon } from "../components/Icons";
import { LabelLayer } from "../components/LabelLayer";
import { ChipPanel } from "../components/Panels";
import { Subtitle } from "../components/Subtitle";
import { easeOutBack, easeOutCubic, ramp, smooth, window } from "../lib/anim";
import { makeCamera, projectToScreen } from "../lib/camera";
import type { Rect } from "../lib/labelLayout";
import { UI } from "../gas-car/Overlay";
import { COLORS, FONT } from "../style/theme";
import { RATIO, TAIL_SPOT } from "./layout";
import { evLabelItems, evLabelSchedule } from "./labels";
import type { EvDrive } from "./mechanics";
import { evCameraPose, evState } from "./state";
import type { EvTimeline } from "./timeline";

/** Same layout slots as the gasoline car (shared UI constants) + EV-only boxes. */
export const EV_UI = {
  ...UI,
  icons: { x0: 640, y0: 40, x1: 1280, y1: 290 } as Rect,
  compare: { x0: 520, y0: 40, x1: 1400, y1: 330 } as Rect,
};

/** Clauses that follow each other closely swap in place; fades only at real pauses (same rule as the gasoline car). */
export const evSubtitle = (tl: EvTimeline, t: number) => {
  const lines = tl.lines;
  const chained = (a?: (typeof lines)[number], b?: (typeof lines)[number]) => !!a && !!b && a.seg === b.seg && b.speechStart - a.speechEnd < 0.9;
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

/** Which on-screen boxes the labels must avoid at time t (shared with the checker). */
export const evReserved = (tl: EvTimeline, t: number, leafBox: Rect | null): Rect[] => {
  const { ev } = tl;
  const r: Rect[] = [EV_UI.subtitle];
  if (t >= ev.dcCurrent - 0.1 && t <= ev.ratioPanel[1]) r.push(EV_UI.topRightPanel);
  if (t >= ev.labelsIn - 0.3 && t <= ev.labelsOut + 0.6) r.push(EV_UI.counter, EV_UI.icons);
  if (t >= ev.compare[0] - 0.1 && t <= ev.compare[1] + 0.1) r.push(EV_UI.compare);
  if (t < tl.seg.title.end + 0.3 || t > tl.seg.end.start - 0.2) r.push(EV_UI.title);
  if (leafBox) r.push(leafBox);
  return r;
};

export const leafBoxAt = (tl: EvTimeline, t: number, width: number, height: number) => {
  if (t < tl.ev.leaf - 0.1 || t > tl.seg.explode.start + 0.4) return null;
  const cam = makeCamera(evCameraPose(tl, t), width, height);
  const p = projectToScreen(cam, TAIL_SPOT, width, height);
  const cx = p.x - 150;
  const cy = p.y + 40;
  return { cx, cy, rect: { x0: cx - 60, y0: cy - 60, x1: cx + 60, y1: cy + 60 } as Rect };
};

export const ElectricCarOverlay: React.FC<{ readonly tl: EvTimeline; readonly drive: EvDrive }> = ({ tl, drive }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const st = evState(tl, drive, frame);
  const t = st.t;
  const { ev, seg } = tl;
  const pose = evCameraPose(tl, t);
  const leaf = leafBoxAt(tl, t, width, height);
  const reserved = evReserved(tl, t, leaf ? leaf.rect : null);
  const items = evLabelItems(evLabelSchedule(tl), st);

  // current direction panel: battery → controller (→ motor once it runs)
  const flowAppear = window(t, ev.dcCurrent, seg.reducer.start + 0.3, 0.35, 0.4);
  const toMotor = st.acCurrent > 0.05;
  const hops = toMotor ? 3 : 2;
  const chase = Math.floor(t * 3) % hops;
  // ratio panel: "rotor 5 turns → wheel 1 turn"; both chips flash each time the wheel completes a turn
  const wheelFrac = (st.drive.wheel / (2 * Math.PI)) % 1;
  const turnFlash = st.drive.omegaW > 0.05 ? Math.max(0, 1 - wheelFrac / 0.18) : 0;
  const ratioAppear = window(t, ev.ratioPanel[0], ev.ratioPanel[1], 0.35, 0.4);

  const iconsAppear = window(t, ev.labelsIn - 0.2, ev.labelsOut + 0.5, 0.3, 0.4);
  const iconPop = (k: number) => (t < ev.icons[k] - 0.05 ? 0 : easeOutBack(ramp(t, ev.icons[k] - 0.05, ev.icons[k] + 0.3), 2.2));
  const iconFocus = (k: number) => window(t, ev.icons[k] - 0.05, ev.icons[k] + 0.75, 0.15, 0.35);
  const counterAppear = window(t, ev.labelsIn - 0.1, ev.labelsOut + 0.5, 0.35, 0.4);
  const compareAppear = window(t, ev.compare[0], ev.compare[1], 0.2, 0.25);
  const leafAppear = leaf ? easeOutBack(ramp(t, ev.leaf, ev.leaf + 0.4), 2) * (1 - smooth(ramp(t, seg.explode.start, seg.explode.start + 0.4))) : 0;
  const sub = evSubtitle(tl, t);

  return (
    <AbsoluteFill>
      <LabelLayer items={items} pose={pose} width={width} height={height} reserved={reserved} />

      <ChipPanel
        title="电流方向"
        color={COLORS.controller}
        appear={flowAppear}
        chips={["电池", "控制器", "电机"].map((label, i) => ({ label, active: i < hops && i === chase ? 1 : 0 }))}
      />
      <ChipPanel
        title="单速减速器 · 只有1个挡"
        color={COLORS.carGreen}
        appear={ratioAppear * (1 - flowAppear)}
        chips={[
          { label: `电机转 ${RATIO} 圈`, active: turnFlash },
          { label: "车轮转 1 圈", active: turnFlash },
        ]}
      />

      {iconsAppear > 0.001 ? (
        <div style={{ position: "absolute", left: EV_UI.icons.x0, top: EV_UI.icons.y0 + 20, width: EV_UI.icons.x1 - EV_UI.icons.x0, display: "flex", justifyContent: "center", gap: 34, opacity: iconsAppear }}>
          <IconCard icon={<BatteryIcon size={110} />} label="电池" color={COLORS.battery} pop={iconPop(0)} focus={iconFocus(0)} />
          <IconCard icon={<MotorIcon size={110} spin={(st.drive.rotor * 180) / Math.PI} />} label="电机" color={COLORS.stator} pop={iconPop(1)} focus={iconFocus(1)} />
          <IconCard icon={<ChipIcon size={110} blink={t * 4} />} label="电控" color={COLORS.controller} pop={iconPop(2)} focus={iconFocus(2)} />
        </div>
      ) : null}
      <Counter
        title="会动的零件"
        target={20}
        plus={false}
        accent={COLORS.carGreen}
        accentDark={COLORS.carGreenDark}
        progress={easeOutCubic(ramp(t, ev.counter[0], ev.counter[0] + 1.6))}
        done={smooth(ramp(t, ev.counter[0] + 1.5, ev.counter[0] + 1.9))}
        appear={counterAppear}
        left={EV_UI.counter.x0}
        top={EV_UI.counter.y0}
      />

      {compareAppear > 0.001 ? (
        <div
          style={{
            position: "absolute",
            left: EV_UI.compare.x0,
            top: EV_UI.compare.y0,
            width: EV_UI.compare.x1 - EV_UI.compare.x0,
            height: EV_UI.compare.y1 - EV_UI.compare.y0,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-around",
            borderRadius: 36,
            background: "rgba(255,255,255,0.95)",
            border: `6px solid ${COLORS.carGreenLight}`,
            boxShadow: "0 10px 26px rgba(34,50,74,0.16)",
            opacity: compareAppear,
            scale: String(0.85 + 0.15 * compareAppear),
            fontFamily: FONT.body,
            fontWeight: 900,
            fontSize: 40,
            color: COLORS.ink,
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <CarSilhouette width={300} color="#B7BEC8" />
              {[0, 1, 2].map((k) => {
                const u = (t * 0.9 + k / 3) % 1;
                return (
                  <div
                    key={k}
                    style={{
                      position: "absolute",
                      left: 14 - 70 * u,
                      top: 92 - 30 * u,
                      width: 26 + 40 * u,
                      height: 26 + 40 * u,
                      borderRadius: "50%",
                      background: COLORS.smoke,
                      opacity: 0.8 * (1 - u),
                    }}
                  />
                );
              })}
            </div>
            <div>汽油车：冒烟</div>
          </div>
          <div style={{ fontSize: 64, color: COLORS.inkSoft }}>VS</div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <CarSilhouette width={300} color={COLORS.carGreen} />
              <div style={{ position: "absolute", left: -46, top: 52 }}>
                <LeafIcon size={64} />
              </div>
            </div>
            <div>电动车：不冒烟</div>
          </div>
        </div>
      ) : null}

      {leaf && leafAppear > 0.001 ? (
        <div style={{ position: "absolute", left: leaf.cx - 50, top: leaf.cy - 50 + 6 * Math.sin(t * 3), scale: String(Math.max(0, leafAppear)), rotate: `${8 * Math.sin(t * 2)}deg` }}>
          <LeafIcon size={100} />
        </div>
      ) : null}

      <BigTitle text="电动车的肚子里有什么？" t={t} start={0.1} end={seg.title.end + 0.25} top={86} border={COLORS.carGreenLight} accent={COLORS.carGreen} />
      <BigTitle text="电动车 = 简单的三大件" t={t} start={seg.end.start + 0.05} end={tl.total + 5} top={86} border={COLORS.carGreenLight} accent={COLORS.carGreen} />

      {sub ? <Subtitle text={sub.text} appear={sub.appear} accent={COLORS.carGreen} /> : null}
    </AbsoluteFill>
  );
};
