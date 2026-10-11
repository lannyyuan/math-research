import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import timeline from './timeline.json';
import {Defs} from './art/ArtView';
import {SCENE_COMPS} from './scenes';
import {PaperOverlay} from './scenes/kit';
import {Subtitle} from './fx/Subtitle';
import './fx/fonts';

export const totalFrames = (fps = timeline.fps) => timeline.scenes.reduce((a, s) => a + Math.round(s.len * fps), 0);

/** subtitles=false：出不带字幕的干净画面（绘本网页用的插图就是这样取的） */
export const Film: React.FC<{subtitles?: boolean}> = ({subtitles = true}) => {
  const {fps} = useVideoConfig();
  let from = 0;
  return (
    <AbsoluteFill style={{background: '#050a22'}}>
      <Defs />
      {timeline.scenes.map((sc) => {
        const Comp = SCENE_COMPS[sc.id];
        const dur = Math.round(sc.len * fps);
        const el = Comp ? (
          <Sequence key={sc.id} from={from} durationInFrames={dur}>
            <Comp len={sc.len} />
          </Sequence>
        ) : null;
        from += dur;
        return el;
      })}
      <PaperOverlay />
      {subtitles ? <Subtitle /> : null}
      {/* 配乐：自己合成的（scripts/make_music.py）。正式渲染时用 --muted 分场景出画面，最后用 ffmpeg 合上整条音轨 */}
      <Audio src={staticFile('audio/score.m4a')} volume={0.9} />
    </AbsoluteFill>
  );
};
