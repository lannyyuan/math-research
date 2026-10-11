import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {CharsCtx} from './fx/Sprite';
import timeline from './timeline.json';
import {SCENE_COMPS} from './scenes';
import {PaperOverlay} from './scenes/kit';
import {Subtitle} from './fx/Subtitle';
import './fx/fonts';

export const totalFrames = (fps = timeline.fps) => timeline.scenes.reduce((a, s) => a + Math.round(s.len * fps), 0);

/** subtitles=false：出不带字幕的干净画面；characters=false：只出背景和光（审计暖色用） */
export const Film: React.FC<{subtitles?: boolean; chars?: boolean; audio?: boolean}> = ({subtitles = true, chars = true, audio = true}) => {
  const {fps} = useVideoConfig();
  let from = 0;
  return (
    <CharsCtx.Provider value={chars}>
    <AbsoluteFill style={{background: '#050a22'}}>
      {audio ? <Audio src={staticFile('audio/score.m4a')} /> : null}
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
    </AbsoluteFill>
    </CharsCtx.Provider>
  );
};
