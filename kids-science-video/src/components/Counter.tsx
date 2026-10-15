import React from "react";
import { COLORS, FONT } from "../style/theme";

/** "会动的零件 ≈ 2000+" style counter card. `progress` 0..1 counts up; `done` shows the "+" and "≈". */
export const Counter: React.FC<{
  readonly title: string;
  readonly target: number;
  readonly progress: number;
  readonly done: number;
  readonly appear: number;
  readonly left: number;
  readonly top: number;
  readonly accent?: string;
  readonly accentDark?: string;
  /** Show the trailing "+" once done (e.g. "≈ 2000+"); false for an exact-ish "≈ 20". */
  readonly plus?: boolean;
}> = ({ title, target, progress, done, appear, left, top, accent = COLORS.carOrange, accentDark = COLORS.carOrangeDark, plus = true }) => {
  if (appear <= 0.001) return null;
  const value = Math.round(target * progress);
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: 470,
        padding: "22px 30px 26px",
        borderRadius: 34,
        background: COLORS.white,
        border: `6px solid ${accent}`,
        boxShadow: "0 10px 26px rgba(34,50,74,0.18)",
        opacity: appear,
        scale: String(0.7 + 0.3 * appear),
        fontFamily: FONT.body,
        color: COLORS.ink,
        textAlign: "center",
        boxSizing: "border-box",
      }}
    >
      <div style={{ fontSize: 40, fontWeight: 900, color: COLORS.inkSoft }}>{title}</div>
      <div style={{ fontSize: 100, fontWeight: 900, lineHeight: 1.05, color: accentDark, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
        <span style={{ fontSize: 64, opacity: done, marginRight: 6 }}>≈</span>
        {value}
        {plus ? <span style={{ opacity: done, display: "inline-block", scale: String(0.4 + 0.6 * done) }}>+</span> : null}
      </div>
    </div>
  );
};
