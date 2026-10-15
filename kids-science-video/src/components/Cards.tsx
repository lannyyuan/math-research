import React from "react";
import { easeOutBack, ramp, smooth } from "../lib/anim";
import { COLORS, FONT, SIZES } from "../style/theme";

/** Big bouncy title (letters drop in one by one). Used for the title card and the end card. */
export const BigTitle: React.FC<{
  readonly text: string;
  readonly t: number;
  readonly start: number;
  readonly end: number;
  readonly top: number;
  readonly size?: number;
  readonly color?: string;
  /** Card border colour and the colour of "=" (defaults: gasoline-car orange). */
  readonly border?: string;
  readonly accent?: string;
}> = ({ text, t, start, end, top, size = SIZES.titleFont, color = COLORS.ink, border = COLORS.carOrangeLight, accent = COLORS.carOrange }) => {
  const out = 1 - smooth(ramp(t, end - 0.35, end));
  if (t < start || out <= 0) return null;
  const chars = [...text];
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, display: "flex", justifyContent: "center", opacity: out }}>
      <div
        style={{
          display: "flex",
          padding: "18px 56px 26px",
          borderRadius: 60,
          background: "rgba(255,255,255,0.86)",
          boxShadow: "0 12px 30px rgba(34,50,74,0.14)",
          border: `6px solid ${border}`,
        }}
      >
        {chars.map((ch, i) => {
          const p = easeOutBack(ramp(t, start + i * 0.045, start + i * 0.045 + 0.4), 2.2);
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                fontFamily: FONT.display,
                fontSize: size,
                lineHeight: 1.15,
                color: ch === "=" ? accent : color,
                opacity: Math.min(1, p * 1.5),
                translate: `0px ${(1 - p) * -60}px`,
                scale: String(Math.max(0, p)),
                WebkitTextStroke: `2px ${COLORS.white}`,
                paddingRight: ch === " " ? size * 0.3 : 0,
              }}
            >
              {ch}
            </span>
          );
        })}
      </div>
    </div>
  );
};
