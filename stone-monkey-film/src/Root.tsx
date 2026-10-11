import React from 'react';
import {Composition} from 'remotion';
import {Film, totalFrames} from './Film';
import timeline from './timeline.json';
import {W, H} from './palette';

export const Root: React.FC = () => (
  <>
    <Composition id="Film" component={Film} durationInFrames={totalFrames()} fps={timeline.fps} width={W} height={H} />
  </>
);
