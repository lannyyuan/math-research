import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Glow} from '../fx/Light';
import {Hazel, Bud, Bolts, Comet, Party} from '../scenes/cast';
import {Bg, PaperOverlay} from '../scenes/kit';
import {W, H} from '../palette';

// 绘本网页的补充插图：影片里没有的章节，用同一套角色（设定图精灵）+ 同一套画笔画的背景再拍一张。
// 渲染：node scripts/book_stills.mjs --only=plate/    （或 npx remotion still src/index.ts Plate out.png --props='{"which":"city"}'）

const Shadow: React.FC<{x: number; y: number; rx?: number}> = ({x, y, rx = 80}) => <GroundShadow x={x} y={y} rx={rx} />;

const City: React.FC = () => (
  <>
    <Bg src="book_city_far.jpg" w={W} h={H} />
    <Shadow x={780} y={900} /><Shadow x={650} y={904} />
    <Bud x={650} y={904} s={0.76} head="bare" walk={4} />
    <Hazel x={780} y={900} s={0.8} walk={4} />
  </>
);

const Castle: React.FC = () => (
  <>
    <Bg src="book_castle_far.jpg" w={W} h={H} />
    {[0, 105, 200, 330].map((d) => <Shadow key={d} x={640 - d} y={966} rx={70} />)}
    <Party x={640} y={962} s={0.66} walking comet={{dx: 330}} bud={{head: 'bare', pocket: true}} bolts={{eyes: 1}} />
  </>
);

const Blanket: React.FC<{x: number; y: number; w: number; h: number}> = ({x, y, w, h}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: '46% 46% 30% 30% / 70% 70% 30% 30%', background: 'repeating-linear-gradient(90deg,#a9bde6 0 38px,#d6e0f5 38px 76px), #a9bde6', boxShadow: 'inset 0 -14px 28px rgba(40,60,120,0.35), 0 8px 26px rgba(10,20,60,0.35)', border: '3px solid rgba(29,36,71,0.7)'}} />
);
const CastleIn: React.FC = () => (
  <>
    <Bg src="book_castle_in_far.jpg" w={W} h={H} />
    <Bolts view="front" x={1180} y={930} s={0.95} eyes={1} />
    <Comet view="side" x={330} y={940} s={0.8} flip={false} />
    <Hazel view="front" x={760} y={1040} s={0.92} clipBottom={0.36} />
    <Bud view="front" x={960} y={1050} s={0.88} head="bare" pocket clipBottom={0.36} />
    <Blanket x={600} y={842} w={540} h={232} />
  </>
);

const Fairground: React.FC = () => (
  <>
    <Bg src="book_fairground_far.jpg" w={W} h={H} />
    {[0, 105, 200, 330].map((d) => <Shadow key={d} x={720 - d} y={986} rx={70} />)}
    <Party x={720} y={982} s={0.66} walking comet={{dx: 330}} bud={{head: 'bare', pocket: true}} bolts={{eyes: 1}} />
  </>
);

const Caravan: React.FC = () => (
  <>
    <Bg src="book_caravan_far.jpg" w={W} h={H} />
    <Comet view="side" x={250} y={940} s={0.74} />
    <Sprite name="pebbles_side" x={470} y={900} s={0.75} flip />
    <Bud view="front" x={820} y={946} s={0.9} head="bare" pocket />
    <Hazel view="front" x={1010} y={940} s={0.95} />
    <Bolts view="front" x={1200} y={940} s={0.9} eyes={1} />
  </>
);

const Dream: React.FC = () => (
  <>
    <Bg src="book_dream_far.jpg" w={W} h={H} />
    <Shadow x={900} y={1000} rx={70} />
    <Hazel view="front" x={900} y={1010} s={0.66} />
  </>
);

const Spring: React.FC = () => (
  <>
    <Bg src="book_spring_far.jpg" w={W} h={H} />
    <Sprite name="pebbles_front_top" x={560} y={856} s={0.55} breathe={0} sway={0} />
    <Shadow x={820} y={1000} rx={90} />
    <Hazel view="side" x={820} y={1000} s={0.9} />
  </>
);

const Dinner: React.FC = () => (
  <>
    <div style={{position: 'absolute', left: -330, top: 0, width: 2400, height: H}}><Bg src="living_far.jpg" w={2400} h={H} /></div>
    <Sprite name="grandad_chair" x={420} y={900} s={0.95} />
    <Shadow x={1080} y={906} rx={230} />
    <Sprite name="table" x={1080} y={906} s={1.0} breathe={0} sway={0} />
    <Bud view="front" x={870} y={900} s={0.8} head="bare" pocket />
    <Hazel view="front" x={1290} y={904} s={0.84} />
    <Sprite name="mallet" x={1590} y={904} s={0.9} />
    <Bolts view="front" x={1080} y={706} s={0.8} eyes={1} />
  </>
);

const Presents: React.FC = () => (
  <>
    <div style={{position: 'absolute', left: -480, top: 0, width: 2400, height: H}}><Bg src="living_far.jpg" w={2400} h={H} /></div>
    <Shadow x={1100} y={910} /><Shadow x={1240} y={914} />
    <Bud view="front" x={1100} y={910} s={0.78} head="bare" pocket />
    <Hazel view="front" x={1250} y={906} s={0.82} />
  </>
);

const MAP: Record<string, React.FC> = {city: City, castle: Castle, castle_in: CastleIn, fairground: Fairground, caravan: Caravan, dream: Dream, spring: Spring, dinner: Dinner, presents: Presents};
const FLURRY: Record<string, number> = {city: 0.6, castle: 0.9, castle_in: 0.0, fairground: 0.9, caravan: 0.0, dream: 0.0, spring: 0.0, dinner: 0.0, presents: 0.0};

export const Plate: React.FC<{which: string}> = ({which}) => {
  const C = MAP[which] ?? City;
  return (
    <AbsoluteFill style={{background: '#0a1230'}}>
      <C />
      {FLURRY[which] > 0 ? <Snow amount={FLURRY[which]} wind={0.15} /> : null}
      <PaperOverlay />
    </AbsoluteFill>
  );
};
