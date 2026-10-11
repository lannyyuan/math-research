import React from 'react';
import {Composition} from 'remotion';
import {Sheet} from './Sheet';
import {Bake} from './bake/Bake';
import {Film, totalFrames} from './Film';
import {Plate} from './plates/Plates';
import timeline from './timeline.json';
import manifest from './bake/manifest.json';
import {W, H} from './palette';

export const Root: React.FC = () => (
  <>
    <Composition id="Film" component={Film} durationInFrames={totalFrames()} fps={timeline.fps} width={W} height={H} />
    <Composition id="Sheet" component={Sheet as React.FC<any>} durationInFrames={60} fps={30} width={W} height={H} defaultProps={{which: 'rabbit'}} />
    <Composition id="Plate" component={Plate as React.FC<any>} durationInFrames={60} fps={30} width={W} height={H} defaultProps={{which: 'shadows'}} />
    <Composition
      id="Bake"
      component={Bake as React.FC<any>}
      durationInFrames={1}
      fps={30}
      width={W}
      height={H}
      defaultProps={{asset: 'paper'}}
      calculateMetadata={({props}: {props: any}) => {
        const m = (manifest as Record<string, {w: number; h: number}>)[props.asset] ?? {w: W, h: H};
        return {width: m.w, height: m.h};
      }}
    />
  </>
);
