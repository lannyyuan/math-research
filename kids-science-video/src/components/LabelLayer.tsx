import React from "react";
import { makeCamera, projectToScreen, type CamPose, type Vec3 } from "../lib/camera";
import { layoutLabels, type LabelPlaced, type Rect } from "../lib/labelLayout";
import { SIZES } from "../style/theme";
import { labelSize, PartLabel } from "./PartLabel";

export type LabelItem = {
  readonly id: string;
  readonly text: string;
  readonly color: string;
  readonly anchor: Vec3;
  /** Preferred screen direction (x right, y down) from anchor to label. */
  readonly dir: readonly [number, number];
  readonly pop: number;
  readonly opacity: number;
  readonly small?: boolean;
  readonly dist?: number;
};

/** Pure: projects + lays out the visible labels. Shared by the renderer and the key-frame checker. */
export const placeLabels = (
  items: readonly LabelItem[],
  pose: CamPose,
  width: number,
  height: number,
  reserved: readonly Rect[],
): (LabelPlaced & { item: LabelItem })[] => {
  const cam = makeCamera(pose, width, height);
  // a label whose part is off screen (or behind the camera) is not shown
  const proj = items.map((i) => projectToScreen(cam, i.anchor, width, height));
  const onScreen = (k: number) => proj[k].visible && proj[k].x > 8 && proj[k].x < width - 8 && proj[k].y > 8 && proj[k].y < height - 8;
  const keep = items.map((i, k) => i.opacity > 0.01 && onScreen(k));
  const vis = items.filter((_, k) => keep[k]);
  const visProj = proj.filter((_, k) => keep[k]);
  const inputs = vis.map((i, k) => {
    const p = visProj[k];
    const { w, h } = labelSize(i.text, i.small);
    return { id: i.id, ax: p.x, ay: p.y, w, h, dx: i.dir[0], dy: i.dir[1], dist: i.dist ?? (i.small ? 110 : 150) };
  });
  const m = SIZES.safeMargin;
  const placed = layoutLabels(inputs, { x0: m, y0: m, x1: width - m, y1: height - m }, reserved);
  return placed.map((p, k) => ({ ...p, item: vis[k] }));
};

export const LabelLayer: React.FC<{
  readonly items: readonly LabelItem[];
  readonly pose: CamPose;
  readonly width: number;
  readonly height: number;
  readonly reserved: readonly Rect[];
}> = ({ items, pose, width, height, reserved }) => {
  const placed = placeLabels(items, pose, width, height, reserved);
  return (
    <>
      {placed.map((p) => (
        <PartLabel
          key={p.id}
          text={p.item.text}
          color={p.item.color}
          cx={p.cx}
          cy={p.cy}
          ax={p.ax}
          ay={p.ay}
          w={p.w}
          h={p.h}
          pop={p.item.pop}
          opacity={p.item.opacity}
          small={p.item.small}
        />
      ))}
    </>
  );
};
