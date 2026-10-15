import React from "react";
import { COLORS, FONT } from "../style/theme";

const chipStyle = (active: number, color: string): React.CSSProperties => ({
  minWidth: 74,
  height: 74,
  padding: "0 14px",
  borderRadius: 37,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontFamily: FONT.body,
  fontWeight: 900,
  fontSize: 38,
  boxSizing: "border-box",
  border: `4px solid ${color}`,
  background: active > 0.5 ? color : COLORS.white,
  color: active > 0.5 ? COLORS.white : COLORS.ink,
  scale: String(1 + 0.18 * active),
  boxShadow: active > 0.05 ? `0 0 ${24 * active}px ${color}` : "none",
});

/** Small top-right info panel with a title and a row of chips (firing order, gear…). */
export const ChipPanel: React.FC<{
  readonly title: string;
  readonly chips: readonly { label: string; active: number }[];
  readonly color: string;
  readonly appear: number;
  readonly right?: number;
  readonly top?: number;
  readonly arrows?: boolean;
}> = ({ title, chips, color, appear, right = 64, top = 56, arrows = true }) => {
  if (appear <= 0.001) return null;
  return (
    <div
      style={{
        position: "absolute",
        right,
        top,
        padding: "16px 26px 22px",
        borderRadius: 30,
        background: "rgba(255,255,255,0.94)",
        border: `5px solid ${color}`,
        boxShadow: "0 8px 22px rgba(34,50,74,0.16)",
        opacity: appear,
        translate: `${(1 - appear) * 40}px 0px`,
        fontFamily: FONT.body,
        color: COLORS.ink,
      }}
    >
      <div style={{ fontSize: 34, fontWeight: 900, marginBottom: 12, textAlign: "center" }}>{title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {chips.map((c, i) => (
          <React.Fragment key={c.label}>
            {arrows && i > 0 ? <span style={{ fontSize: 30, fontWeight: 900, color: COLORS.inkSoft }}>→</span> : null}
            <div style={chipStyle(c.active, color)}>{c.label}</div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

/** Small round number tag that floats over a 3D point (e.g. cylinder numbers). */
export const NumberTag: React.FC<{ readonly x: number; readonly y: number; readonly label: string; readonly active: number; readonly appear: number }> = ({
  x,
  y,
  label,
  active,
  appear,
}) => {
  if (appear <= 0.001) return null;
  const size = 50;
  return (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: FONT.body,
        fontWeight: 900,
        fontSize: 30,
        background: active > 0.5 ? COLORS.highlight : COLORS.white,
        border: `4px solid ${active > 0.5 ? COLORS.carOrange : COLORS.ink}`,
        color: COLORS.ink,
        opacity: appear,
        scale: String(1 + 0.3 * active),
        boxShadow: active > 0.05 ? `0 0 ${26 * active}px ${COLORS.highlight}` : "none",
      }}
    >
      {label}
    </div>
  );
};
