import React from 'react';
import {Composition} from 'remotion';
import {Film, totalFrames} from './Film';
import timeline from './timeline.json';
import {W, H} from './palette';
import {Plate} from './plates/Plate';

export const Root: React.FC = () => (
  <>
    <Composition id="Film" component={Film} durationInFrames={totalFrames()} fps={timeline.fps} width={W} height={H} />
    <Composition id="Plate" component={Plate} durationInFrames={30} fps={timeline.fps} width={W} height={H} defaultProps={{which: 'city'}} />
  </>
);
