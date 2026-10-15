import React from "react";
import { COLORS, FONT, SIZES } from "../style/theme";

export type PartLabelProps = {
  readonly text: string;
  readonly color: string;
  /** Label centre (px). */
  readonly cx: number;
  readonly cy: number;
  /** Anchor point on the part (px). */
  readonly ax: number;
  readonly ay: number;
  readonly w: number;
  readonly h: number;
  /** 0..1(+) pop-in amount (may overshoot for a springy feel). */
  readonly pop: number;
  readonly opacity: number;
  readonly small?: boolean;
};

/** Chinese callout: rounded card + leader line + anchor dot. Always faces the viewer (2D overlay). */
export const PartLabel: React.FC<PartLabelProps> = ({ text, color, cx, cy, ax, ay, w, h, pop, opacity, small }) => {
  // leader line ends at the nearest point of the card's border
  const ex = Math.max(cx - w / 2, Math.min(cx + w / 2, ax));
  const ey = Math.max(cy - h / 2, Math.min(cy + h / 2, ay));
  const fs = small ? SIZES.labelFontSmall : SIZES.labelFont;
  return (
    <div style={{ position: "absolute", inset: 0, opacity, pointerEvents: "none" }}>
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <line x1={ax} y1={ay} x2={ex} y2={ey} stroke={COLORS.white} strokeWidth={7} strokeLinecap="round" opacity={Math.min(1, pop)} />
        <line x1={ax} y1={ay} x2={ex} y2={ey} stroke={COLORS.ink} strokeWidth={3} strokeLinecap="round" opacity={Math.min(1, pop)} />
        <circle cx={ax} cy={ay} r={9 * Math.min(1, pop)} fill={color} stroke={COLORS.white} strokeWidth={3.5} />
      </svg>
      <div
        style={{
          position: "absolute",
          left: cx - w / 2,
          top: cy - h / 2,
          width: w,
          height: h,
          scale: String(0.55 + 0.45 * pop),
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          background: COLORS.white,
          borderRadius: h / 2,
          border: `4px solid ${color}`,
          boxShadow: "0 6px 16px rgba(34,50,74,0.18)",
          fontFamily: FONT.body,
          fontWeight: 900,
          fontSize: fs,
          color: COLORS.ink,
          whiteSpace: "nowrap",
          boxSizing: "border-box",
        }}
      >
        <span style={{ width: fs * 0.42, height: fs * 0.42, borderRadius: "50%", background: color, flex: "none" }} />
        {text}
      </div>
    </div>
  );
};

/** Card size for a label (CJK glyphs are ~1em wide). */
export const labelSize = (text: string, small?: boolean) => {
  const fs = small ? SIZES.labelFontSmall : SIZES.labelFont;
  const chars = [...text].reduce((n, ch) => n + (/[\u0000-ÿ]/.test(ch) ? 0.6 : 1), 0);
  return { w: Math.round(chars * fs + fs * 0.42 + 10 + 2 * 22 + 8), h: Math.round(fs * 1.62) };
};
