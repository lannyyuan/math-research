import React from "react";
import { Composition, Folder } from "remotion";
import { EV_TL } from "./electric-car/data";
import { ElectricCarVideo } from "./electric-car/ElectricCarVideo";
import { GAS_TL } from "./gas-car/data";
import { GasCarVideo } from "./gas-car/GasCarVideo";
import "./style/fonts";

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Folder name="GasCar">
      <Composition
        id="GasCarVoice"
        component={GasCarVideo}
        durationInFrames={GAS_TL.totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ narration: true }}
      />
      <Composition
        id="GasCarSubtitles"
        component={GasCarVideo}
        durationInFrames={GAS_TL.totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ narration: false }}
      />
    </Folder>
    <Folder name="ElectricCar">
      <Composition
        id="ElectricCarVoice"
        component={ElectricCarVideo}
        durationInFrames={EV_TL.totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ narration: true }}
      />
      <Composition
        id="ElectricCarSubtitles"
        component={ElectricCarVideo}
        durationInFrames={EV_TL.totalFrames}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ narration: false }}
      />
    </Folder>
    </>
  );
};
