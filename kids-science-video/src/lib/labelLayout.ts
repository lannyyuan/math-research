/**
 * Deterministic 2D label placement: start each label at its preferred offset
 * from its anchor, then iteratively separate overlapping boxes and keep them
 * inside the safe area / out of reserved regions. Pure function of its input,
 * so the same frame always yields the same layout.
 */
export type Rect = { x0: number; y0: number; x1: number; y1: number };

export type LabelInput = {
  readonly id: string;
  /** Anchor in screen pixels. */
  readonly ax: number;
  readonly ay: number;
  readonly w: number;
  readonly h: number;
  /** Preferred direction from anchor to the label centre (need not be normalised). */
  readonly dx: number;
  readonly dy: number;
  /** Preferred anchor → label-centre distance in pixels. */
  readonly dist: number;
};

export type LabelPlaced = LabelInput & { readonly cx: number; readonly cy: number };

const overlap = (a: Rect, b: Rect) =>
  Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0) > 0 && Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) > 0;

export const rectOf = (l: { cx: number; cy: number; w: number; h: number }, pad = 0): Rect => ({
  x0: l.cx - l.w / 2 - pad,
  y0: l.cy - l.h / 2 - pad,
  x1: l.cx + l.w / 2 + pad,
  y1: l.cy + l.h / 2 + pad,
});

export const layoutLabels = (
  labels: readonly LabelInput[],
  bounds: Rect,
  reserved: readonly Rect[] = [],
  gap = 14,
  iterations = 160,
): LabelPlaced[] => {
  const pos = labels.map((l) => {
    const n = Math.hypot(l.dx, l.dy) || 1;
    return { x: l.ax + (l.dx / n) * l.dist, y: l.ay + (l.dy / n) * l.dist };
  });
  const pref = pos.map((p) => ({ ...p }));

  const clampIn = (i: number) => {
    const l = labels[i];
    pos[i].x = Math.min(bounds.x1 - l.w / 2, Math.max(bounds.x0 + l.w / 2, pos[i].x));
    pos[i].y = Math.min(bounds.y1 - l.h / 2, Math.max(bounds.y0 + l.h / 2, pos[i].y));
  };

  for (let it = 0; it < iterations; it++) {
    // weak spring back to the preferred spot keeps labels near their part
    for (let i = 0; i < labels.length; i++) {
      pos[i].x += (pref[i].x - pos[i].x) * 0.02;
      pos[i].y += (pref[i].y - pos[i].y) * 0.02;
    }
    for (let i = 0; i < labels.length; i++) {
      for (let j = i + 1; j < labels.length; j++) {
        const a = labels[i];
        const b = labels[j];
        const ox = (a.w + b.w) / 2 + gap - Math.abs(pos[i].x - pos[j].x);
        const oy = (a.h + b.h) / 2 + gap - Math.abs(pos[i].y - pos[j].y);
        if (ox > 0 && oy > 0) {
          // push along the axis of least penetration; ties broken by index → deterministic
          if (ox * 0.6 < oy) {
            const s = pos[i].x < pos[j].x || (pos[i].x === pos[j].x && i < j) ? -1 : 1;
            pos[i].x += (s * ox) / 2;
            pos[j].x -= (s * ox) / 2;
          } else {
            const s = pos[i].y < pos[j].y || (pos[i].y === pos[j].y && i < j) ? -1 : 1;
            pos[i].y += (s * oy) / 2;
            pos[j].y -= (s * oy) / 2;
          }
        }
      }
      for (const r of reserved) {
        const l = labels[i];
        const ox = Math.min(pos[i].x + l.w / 2 + gap, r.x1) - Math.max(pos[i].x - l.w / 2 - gap, r.x0);
        const oy = Math.min(pos[i].y + l.h / 2 + gap, r.y1) - Math.max(pos[i].y - l.h / 2 - gap, r.y0);
        if (ox > 0 && oy > 0) {
          const rcx = (r.x0 + r.x1) / 2;
          const rcy = (r.y0 + r.y1) / 2;
          if (ox < oy) pos[i].x += pos[i].x < rcx ? -ox : ox;
          else pos[i].y += pos[i].y < rcy ? -oy : oy;
        }
      }
      clampIn(i);
    }
  }
  return labels.map((l, i) => ({ ...l, cx: pos[i].x, cy: pos[i].y }));
};

/** Used by the key-frame self check: returns overlapping pairs (should be empty). */
export const findOverlaps = (placed: readonly LabelPlaced[], pad = 0) => {
  const out: [string, string][] = [];
  for (let i = 0; i < placed.length; i++)
    for (let j = i + 1; j < placed.length; j++)
      if (overlap(rectOf(placed[i], pad), rectOf(placed[j], pad))) out.push([placed[i].id, placed[j].id]);
  return out;
};
