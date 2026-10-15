import { useThree } from "@react-three/fiber";
import React, { useLayoutEffect } from "react";
import type { PerspectiveCamera } from "three";
import type { CamPose } from "../lib/camera";

/** Applies a precomputed (frame-driven) camera pose to the R3F default camera. */
export const CameraRig: React.FC<{ readonly pose: CamPose }> = ({ pose }) => {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  const size = useThree((s) => s.size);
  useLayoutEffect(() => {
    camera.position.set(...pose.pos);
    camera.up.set(0, 1, 0);
    camera.lookAt(...pose.target);
    camera.fov = pose.fov;
    camera.aspect = size.width / size.height;
    camera.near = 0.05;
    camera.far = 200;
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld(true);
  });
  return null;
};
