import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {Defs} from './art/ArtView';
import {Rabbit} from './chars/Rabbit';
import {Boy} from './chars/Boy';
import {Turtle, TurtleHead} from './chars/Turtle';
import {Deer} from './chars/Deer';
import {OldMan, Wolf, Cub} from './chars/Others';
import {C, W, H} from './palette';

// 角色设定检查用：白底 / 夜空两种背景下看角色
export const Sheet: React.FC<{which: string}> = ({which}) => {
  if (which === 'world') {
    return (
      <AbsoluteFill style={{background: '#000'}}>
        <Defs />
        <Img src={staticFile('baked/sky-night.jpg')} style={{position: 'absolute', left: -192, top: -80, width: 2304, height: 1296}} />
        <Img src={staticFile('baked/trees-far.png')} style={{position: 'absolute', left: -300, top: 270, width: 3400, height: 420}} />
        <Img src={staticFile('baked/trees-mid.png')} style={{position: 'absolute', left: -600, top: 180, width: 3400, height: 520}} />
        <Img src={staticFile('baked/snow-a.png')} style={{position: 'absolute', left: -300, top: 620, width: 3400, height: 700}} />
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute'}}>
          <Rabbit x={900} y={880} s={0.9} />
        </svg>
        <Img src={staticFile('baked/paper.jpg')} style={{position: 'absolute', inset: 0, width: W, height: H, mixBlendMode: 'overlay', opacity: 0.9}} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{background: C.snow}}>
      <Defs />
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <rect x={0} y={0} width={W} height={H / 2} fill={C.skyMid} />
        <rect x={0} y={H / 2} width={W} height={H / 2} fill={C.snow} />
        {which === 'boy' && (
          <>
            <Boy x={350} y={1000} s={3.6} walk={0} />
            <Boy x={1000} y={1000} s={2.6} walk={1} t0={0.1} />
            <Boy x={1250} y={950} s={1} walk={1} />
            <Boy x={1450} y={950} s={0.5} walk={1} flip />
            <Rabbit x={1700} y={950} s={0.8} />
          </>
        )}
        {which === 'deer' && (
          <>
            <Deer x={560} y={980} s={1.3} walk={0} />
            <Deer x={1500} y={980} s={0.7} walk={1} flip leaves={1} headDown={0.4} />
          </>
        )}
        {which === 'turtle' && (
          <>
            <Turtle x={500} y={900} s={3} snow={1} />
            <Turtle x={1250} y={900} s={3} snow={0} />
            <Boy x={1700} y={950} s={1.2}><TurtleHead x={-42} y={-190} /></Boy>
          </>
        )}
        {which === 'others' && (
          <>
            <OldMan x={260} y={980} s={1.5} />
            <Wolf x={800} y={980} s={1.6} />
            <Cub x={1230} y={980} s={1.8} />
            <Boy x={1500} y={980} s={1.2} variant="dad" />
            <Boy x={1680} y={980} s={1.1} variant="mom" flip />
            <Boy x={1830} y={980} s={0.7} variant="shirt" />
          </>
        )}
        {which === 'rabbit' && (
          <>
            <Rabbit x={400} y={900} s={3} perk={0.8} />
            <Rabbit x={1500} y={900} s={0.7} flip t0={1} />
            <Rabbit x={1100} y={900} s={3} fear={1} t0={2} />
            <Rabbit x={1700} y={900} s={1.2} flip />
          </>
        )}
      </svg>
    </AbsoluteFill>
  );
};
